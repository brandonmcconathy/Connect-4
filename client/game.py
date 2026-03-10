import json
import os
import random
from abc import ABC, abstractmethod
from ai import AI

class ConnectionError(Exception):
    """Raised when client gets disconnected from the server"""
    pass

class Game(ABC):

    def __init__(self):
        self.player_num = None
        self.game_over = False
        self.won = None
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
        print("You are player %d" %self.player_num)
        print("You will have the symbol %s" %('X' if self.player_num == 1 else 'O'))

    def take_turn(self):
        turn_bytes = self.socket.recv(4096)
        if not turn_bytes:
            raise ConnectionError
        turn_data = json.loads(turn_bytes.decode())
        self.board = turn_data["board"]
        if turn_data["is_active"]:
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
            
class LocalGame(Game):

    def __init__(self):
        super().__init__()
        self.ai = AI()
        self.active = None
        self.last_move = None

    def set_active(self):
        self.active = True if self.player_num == 1 else False

    def update_board(self, column, symbol):
        # Updates lowest empty row in given column
        row_to_update = 0
        for i, row in enumerate(self.board):
            if row[column] == ' ':
                row_to_update = i
        self.board[row_to_update][column] = symbol
        self.last_move = (row_to_update, column)

    def take_turn(self):
        if self.active:
            print("It's your turn!")
            column = input("Enter a column number from 1-7: ")
            while not self.validate_column(column):
                print("Invalid Input")
                column = input("Enter a column number from 1-7: ")
            column = int(column) - 1    # Column is 0-indexed          
            self.update_board(column, 'X')
        else:
            # Take AI turn
            print("Please wait for the AI to take its turn.")
            column = self.ai.take_turn()
            self.update_board(column, 'O')
        
        self.print_board()
        
        # Checks if someone won and assigns a winner
        self.check_win()
        if self.game_over:
            self.won = self.active
        
        self.active = not self.active

    def check_win(self):
        row = self.last_move[0]
        col = self.last_move[1]
        last_symbol = self.board[row][col]

        # Check horizontal
        left_bound = max(0, col - 3)
        for i in range(left_bound, col + 1):
            win = True
            for j in range(4):
                if j + i < 7:
                    if self.board[row][j + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return

        # Check Vertical
        top_bound = max(0, row - 3)
        for i in range(top_bound, row + 1):
            win = True
            for j in range(4):
                if j + i < 6:
                    if self.board[j + i][col] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return

        # Check Positive Diagonal
        min_row = row
        min_col = col
        for i in range(3):
            if min_row != 5 and min_col != 0:
                min_row += 1
                min_col -= 1

        col_i = min_col
        for row_i in range(min_row, row, -1):
            win = True
            for i in range(4):
                if row_i - i >= 0 and col_i + i < 7:
                    if self.board[row_i - i][col_i + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return
            col_i += 1

        # Check Negative Diagonal
        min_row = row
        min_col = col
        for i in range(3):
            if min_row != 0 and min_col != 0:
                min_row -= 1
                min_col -= 1

        col_i = min_col
        for row_i in range(min_row, row):
            win = True
            for i in range(4):
                if row_i + i < 6 and col_i + i < 7:
                    if self.board[row_i + i][col_i + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return
            col_i += 1

        # Did not detect win
        self.game_over = False
        
    def play_game(self):
        self.get_player_num()
        self.set_active()
        self.print_board()
        while True:
            self.take_turn()
            if self.game_over:
                self.end_game()
                break
