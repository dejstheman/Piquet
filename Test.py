from copy import deepcopy

import HandStatistics
from Card import Card
from Deck import Deck
from Hand import Hand


def get_opponent_maximum_point(hand):

    aces = [card for card in hand.cards if card.rank == 8]

    point_set = sorted([card for card in hand.points if card in hand.get_best_set()])
    point_set_seq = sorted([card for card in hand.points if card in hand.get_best_sequence() and card not in point_set])
    point_set_seq_aces = sorted([card for card in hand.points if any(True for ace in aces if ace.suit == card.suit)
                                 and card not in point_set + point_set_seq])
    point = sorted([card for card in hand.points if card not in point_set + point_set_seq + point_set_seq_aces])
    remaining_cards = sorted([card for card in hand.cards if
                              card not in point_set + point_set_seq + point_set_seq_aces + point])

    untouchables = []

    while len(untouchables) != 4:
        if point_set_seq_aces:
            untouchables.append(point_set_seq_aces.pop(-1))
        elif point_set_seq:
            untouchables.append(point_set_seq.pop(-1))
        elif point_set:
            untouchables.append(point_set.pop(-1))
        elif point:
            untouchables.append(point.pop(-1))
        else:
            untouchables.append(remaining_cards.pop(-1))

    return [card for card in hand.cards if card not in untouchables]


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

    # cards = Deck().cards[:12]

    hand = Hand(cards)
    print(HandStatistics.compute_point_discard(hand, 8, 0))
    print(HandStatistics.compute_greedy_discard(hand, 5))
