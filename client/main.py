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
        self.online = None
        self.difficulty = None
        self.game = Game()

    def set_opponent(self):
        user_input = input("Would you like to play online or against an AI? (o for online, a for AI): ")
        while not self.validate_online_input(user_input):
            print("Sorry that response was invalid.")
            user_input = input("Would you like to play online or against an AI? (o for online, a for AI): ")
        self.online = True if user_input == 'o' or user_input == 'O' else False
        if not self.online:
            user_input = input("What difficulty do you want to play against? (1 for easy, 2 for medium, 3 for hard, 4 for expert): ")
            while not self.validate_difficulty(user_input):
                print("Sorry that response was invalid.")
                user_input = input("What difficulty do you want to play against? (1 for easy, 2 for medium, 3 for hard, 4 for expert): ")
            self.difficulty = user_input

    def validate_online_input(self, user_input):
        if user_input == 'o' or user_input == 'O' or user_input == 'a' or user_input == 'A':
            return True
        return False
    
    def validate_difficulty(self, difficulty):
        if not difficulty.isdigit():
            return False
        difficulty = int(difficulty)
        if difficulty < 1 or difficulty > 4:
            return False
        
        return True

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
    client.set_opponent()
    client.connect_to_server()
    client.start_game()
    client.handle_disconnection()
        
