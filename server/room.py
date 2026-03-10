

class Room:

    def __init__(self):
        self.players = []

    def get_num_players(self):
        return len(self.players)
    
    def add_player(self, player):
        self.players.append(player)

class SinglePlayerRoom():

    def __init__(self, player=None):
        self.player = player

    def add_player(self, player):
        self.player = player
