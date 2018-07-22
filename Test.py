import HandStatistics
from Card import Card
from Deck import Deck
from Hand import Hand


def get_opponent_maximum_point():
    hand = Hand(Deck().cards[0:12])

    return HandStatistics.compute_opponent_maximum_set(hand, rank=8)


if __name__ == "__main__":
    points = get_opponent_maximum_point()
    print(points)
