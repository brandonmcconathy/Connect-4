import random

class AI:

    def __init__(self):
        self.symbol = None

    def take_turn(self):
        return random.randint(0, 6)