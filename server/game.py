import json
import random

class Game:

    def __init__(self, room):
        self.room = room
        self.player1 = None
        self.plyer2 = None

    def assign_players(self):
        # Randomly assign players a player number
        first_player = random.randint(0, 1)
        self.player1 = self.room.players[first_player]
        self.player2 = self.room.players[0 if first_player else 1]

        # Send player 1 their player number
        player1_data = json.dumps({"player_num": 1}).encode()
        self.player1.socket.send(player1_data)

        # Send player 2 their player number
        player2_data = json.dumps({"player_num": 2}).encode()
        self.player2.socket.send(player2_data)
        

    def start_game(self):
        self.assign_players()

