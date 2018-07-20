class Card:

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __key__(self):
        return self.rank, self.suit

    def __repr__(self):
        return str(self.rank) + self.suit

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __ne__(self, other):
        return self.rank != other.rank or self.suit != other.suit

    def __gt__(self, other):
        return self.rank > other.rank

    def __lt__(self, other):
        return self.rank < other.rank

    def __hash__(self):
        return hash(self.__key__())

