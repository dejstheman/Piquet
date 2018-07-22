import random
from copy import deepcopy

import HandStatistics
from Card import Card
from Deck import Deck
from Hand import Hand


def get_opponent_maximum_point(hand):
    lst1 = [3, 0, 2]
    lst2 = [3, 1, 2]
    com = list(zip(lst1, lst2))
    comps = [j == i for i, j in com if i > 0]
    print(comps)

    return all(comps)


if __name__ == "__main__":
    cards = []
    cards.append(Card(4, 'H'))
    cards.append(Card(7, 'H'))
    cards.append(Card(6, 'H'))
    cards.append(Card(5, 'H'))
    cards.append(Card(2, 'H'))
    cards.append(Card(8, 'C'))
    cards.append(Card(7, 'C'))
    cards.append(Card(2, 'C'))
    cards.append(Card(8, 'D'))
    cards.append(Card(7, 'S'))
    cards.append(Card(3, 'S'))
    cards.append(Card(6, 'S'))

    cards = Deck().cards[:12]
    hand = Hand(cards)
    print(get_opponent_maximum_point(hand))

