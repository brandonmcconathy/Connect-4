import socket
import os
import signal
import json

from game import Game
from room import Room
from connectionerror import ConnectionError

class Player:

    def __init__(self, socket):
        self.socket = socket
        self.symbol = ''


class Server:

    def __init__(self):
        self.port = 50000       # Random port
        self.socket = None
        self.curr_room = Room()

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(5)
        print("Server Started. Listening for connections on port %d." %self.port)

        # Sets up signal to remove zombie processes
        signal.signal(signal.SIGCHLD, self.reap_children)

    def accept_new_connection(self):
        connection, address = self.socket.accept()
        print("New connection: ", address)
        try:
            self.put_new_connection_in_room(connection)
        except ConnectionError:
            self.curr_room = Room()
            self.put_new_connection_in_room(connection)

    def put_new_connection_in_room(self, new_socket):
        # Make new player
        player = Player(new_socket)

        # Add player to empty room
        if self.curr_room.get_num_players() == 0:
            self.curr_room.add_player(player)
            return

        # Add player to room with player in it already
        if self.curr_room.get_num_players() == 1:

            # Make sure curr player in room is still active
            pending_player = self.curr_room.get_pending_player()
            try:
                message_data = json.dumps({"send-keep-alive": True}).encode()
                pending_player.socket.send(message_data)
            except BrokenPipeError:
                raise ConnectionError
            keep_alive_bytes = pending_player.socket.recv(4096)
            if not keep_alive_bytes:
                # Connection closed
                raise ConnectionError
            keep_alive_data = json.loads(keep_alive_bytes.decode())
            if not keep_alive_data["keep-alive"]:
                raise ConnectionError
            
            # Make sure new player in room is still active
            try:
                message_data = json.dumps({"send-keep-alive": True}).encode()
                new_socket.send(message_data)
            except BrokenPipeError:
                raise ConnectionError
            keep_alive_bytes = new_socket.recv(4096)
            if not keep_alive_bytes:
                # Connection closed
                raise ConnectionError
            keep_alive_data = json.loads(keep_alive_bytes.decode())
            if not keep_alive_data["keep-alive"]:
                raise ConnectionError

            # Add new player to room
            self.curr_room.add_player(player)
            
            # Start room process
            newpid = os.fork()
            if newpid == 0:
                # Move process to game loop
                new_game = Game(self.curr_room)
                new_game.start_game()   # Room process will exit and never return here

            print("Starting new multiplayer room process with pid: ", newpid)
            return
        
        # curr_room is full. Add player to new room
        new_room = Room()
        new_room.add_player(player)
        self.curr_room = new_room

    def reap_children(self, signum, frame):
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
            except OSError:
                break


if __name__ == "__main__":
    server = Server()
    server.start_server()
    while True:
        try:
            server.accept_new_connection()
        except ConnectionError:
            pass
