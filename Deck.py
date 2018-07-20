import random

from Card import Card


class Deck:

    def __init__(self):
        self.ranks = range(1, 9)
        self.suits = ["C", "D", "H", "S"]
        self.cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards[0:12], self.cards[12:24], self.cards[24:32]
