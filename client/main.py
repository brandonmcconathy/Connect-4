import socket

from game import Game

class ConnectionError(Exception):
    """Raised when client gets disconnected from the server"""
    pass

class Client:

    def __init__(self):
        self.server_host = "localhost"
        self.server_port = 50000
        self.socket = None
        self.game = Game()

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))
        self.game.set_socket(self.socket)

    def start_game(self):
        self.game.play_game()

    def handle_disconnection(self):
        self.socket.close()
        print("You have been disconnected from the server.")

if __name__ == "__main__":
    client = Client()
    client.connect_to_server()
    client.start_game()
    client.handle_disconnection()
        
