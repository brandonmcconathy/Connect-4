import json
import os
import random
from abc import ABC, abstractmethod

class ConnectionError(Exception):
    """Raised when client gets disconnected from the server"""
    pass

class Game(ABC):

    def __init__(self):
        self.player_num = None
        self.game_over = False
        self.won = None
        self.is_active = None
        self.board = [[' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' ']]
        
    def get_player_num(self):
        self.player_num = random.randint(1, 2)
        print("You are player %d" %self.player_num)
        print("You will have the symbol X")

    def validate_column(self, column):
        if not column.isdigit():
            return False
        column = int(column)
        if column < 1 or column > 7:
            return False
        
        # Checks if column is already full
        if self.board[0][column - 1] != ' ':
            return False
        
        return True
    
    @abstractmethod
    def take_turn(self):
        pass

    def print_board(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("---------------")
        for row in self.board:
            print('|', end="")
            for col in row:
                print(col, end="|")
            
            print("\n---------------")

    def end_game(self):
        if self.won:
            print("Congratulations! You won!")
        else:
            print("You lose. Better luck next time.")

    @abstractmethod
    def play_game(self):
        pass
            
class OnlineGame(Game):

    def __init__(self):
        super().__init__()
        self.socket = None

    def set_socket(self, socket):
        self.socket = socket

    def get_player_num(self):
        data = self.socket.recv(4096)
        json_data = json.loads(data.decode())
        self.player_num = json_data["player_num"]
        self.is_active = json_data["is_active"]
        print("You are player %d" %self.player_num)
        print("You will have the symbol %s" %('X' if self.player_num == 1 else 'O'))

    def take_turn(self):
        if self.is_active:
            # Make move
            print("It's your turn!")
            column = input("Enter a column number from 1-7: ")

            # Validate input
            while not self.validate_column(column):
                print("Invalid Input")
                column = input("Enter a column number from 1-7: ")
            column = int(column) - 1                    # -1 because board is 0-indexed
            column_data = json.dumps({"column": column}).encode()
            self.socket.send(column_data)

        else:
            print("Please wait for the other player to make their move.")

        # Wait for updated board
        board_bytes = self.socket.recv(4096)
        if not board_bytes:
            raise ConnectionError
        board_data = json.loads(board_bytes.decode())
        self.board = board_data["board"]
        self.print_board()

        if board_data["game_over"]:
            self.game_over = True
            self.won = True if board_data["won"] else False

        self.is_active = not self.is_active

    def play_game(self):
        print("Connected to server. Waiting for another player to join...")
        self.get_player_num()
        self.print_board()
        while True:
            try:
                self.take_turn()
            except ConnectionError:
                return
            if self.game_over:
                self.end_game()
                return
            