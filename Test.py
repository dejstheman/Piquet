import random
from copy import deepcopy
from itertools import combinations

import HandStatistics
from Card import Card
from DealState import check_sample_hand
from Deck import Deck
from Hand import Hand


def get_opponent_maximum_point(target, known_cards, unseen_cards, hand_length):
    valid = []
    for x in combinations(unseen_cards, hand_length):
        hand = Hand(known_cards + x)
        sample = [hand.get_point_value()]
        if check_sample_hand(target, sample):
            valid += x
    return random.choice(valid)


if __name__ == "__main__":
    # cards = []
    # cards.append(Card(4, 'H'))
    # cards.append(Card(7, 'H'))
    # cards.append(Card(6, 'H'))
    # cards.append(Card(5, 'H'))
    # cards.append(Card(2, 'H'))
    # cards.append(Card(8, 'C'))
    # cards.append(Card(7, 'C'))
    # cards.append(Card(2, 'C'))
    # cards.append(Card(8, 'D'))
    # cards.append(Card(7, 'S'))
    # cards.append(Card(3, 'S'))
    # cards.append(Card(6, 'S'))
    #
    # cards = Deck().cards[:12]
    # hand = Hand(cards)
    # print(get_opponent_maximum_point(hand))

    for x in range(1, 13):
        print(x, len(list(combinations(range(17), x))))

