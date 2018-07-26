import random
from copy import deepcopy

from more_itertools import consecutive_groups

from Card import Card
from Deck import Deck
from HandStatistics import compute_point, compute_sequences, compute_sets, compute_best_group


def get_longest_sub_sequence(lst):
    s = {x for x in lst}
    length = 0
    for i in range(len(lst)):
        if lst[i] - 1 not in s:
            j = lst[i]
            while j in s:
                j += 1
            length = max(length, j - lst[i])
    return length


class Hand:

    def __init__(self, cards):
        self.cards = cards
        self.points, self.sequences, self.sets = self.__compute_stats()

    def __compute_stats(self):
        return compute_point(self), compute_sequences(self), compute_sets(self)

    def remove_cards(self, cards):
        self.cards = [card for card in self.cards if card not in cards]

    def add_cards(self, cards):
        self.cards += cards
        self.points, self.sequences, self.sets = self.__compute_stats()

    def get_point_value(self):
        return len(self.points)

    def get_point_sum(self):
        total = 0
        for card in self.points:
            if card.rank == 8:
                total += 11
            elif card.rank in range(5, 8):
                total += 10
            else:
                total += card.rank + 6
        return total

    def get_best_sequence(self):
        return compute_best_group(self.sequences)

    def get_sequence_value(self):
        length = len(self.get_best_sequence())
        return length if length < 5 else length + 10

    def get_sequence_rank(self):
        return max(self.get_best_sequence()) if self.get_best_sequence() else Card(0, 'X')

    def get_other_sequence_values(self):
        return [len(seq) if len(seq) < 5 else len(seq) + 10
                for seq in self.sequences if seq != self.get_best_sequence()]

    def get_best_set(self):
        return compute_best_group(self.sets)

    def get_set_value(self):
        length = len(self.get_best_set())
        return length if length < 4 else length + 10

    def get_set_rank(self):
        return max(self.get_best_set()) if self.get_best_set() else Card(0, 'X')

    def get_other_set_values(self):
        return [len(s) if len(s) < 5 else len(s) + 10 for s in self.sets if s != self.get_best_set()]

    def get_value(self):
        return self.get_point_value() + self.get_sequence_value() + self.get_set_value()

    def get_remaining_cards(self):
        return [card for card in Deck().cards if card not in self.cards]

    def add_point_increasing_card(self):
        suit_points = {card.suit: len([c for c in self.cards if c.suit == card.suit]) for card in self.cards}
        point_sorted_suit = [p[0] for p in sorted(suit_points.items(), key=lambda x: x[1], reverse=True)]
        for suit in point_sorted_suit:
            for card in [c for c in self.get_remaining_cards() if c.suit == suit]:
                temp = Hand(deepcopy(self.cards))
                temp.cards.append(card)
                if temp.get_sequence_value() == self.get_sequence_value() \
                        and temp.get_set_value() == self.get_set_value():
                    self.cards.append(card)
                    self.points, self.sequences, self.sets = self.__compute_stats()
                    return

    def add_sequence_increasing_card(self):
        suit_seqs = {suit: max([list(g)
                                for g in consecutive_groups(
                sorted([card.rank for card in hand.cards if card.suit == suit]))],
                               key=lambda g: len(g)) for suit in {card.suit for card in self.cards}}
        seq_sorted_suits = [p[0] for p in sorted(suit_seqs.items(), key=lambda x: len(x[1]), reverse=True)]

        for suit in seq_sorted_suits:
            cards = sorted([card.rank for card in self.cards if card.suit == suit])
            missing = sorted(set(range(1, 9)).difference(cards))
            sub_seqs = {}
            for c in missing:
                temp = deepcopy(cards)
                temp.append(c)
                sub_seqs[c] = get_longest_sub_sequence(sorted(temp))
            sub_seqs_sorted = [p[0] for p in sorted(sub_seqs.items(), key=lambda x: x[1], reverse=True)]
            for rank in sub_seqs_sorted:
                for card in [card for card in self.get_remaining_cards() if card.suit == suit]:
                    if card.rank == rank:
                        temp = Hand(deepcopy(self.cards))
                        temp.cards.append(card)
                        if temp.get_point_value() == self.get_point_value() and temp.get_set_value() == self.get_set_value():
                            self.cards.append(card)
                            self.points, self.sequences, self.sets = self.__compute_stats()
                            return

    def __repr__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)


if __name__ == "__main__":
    cards = []
    cards.append(Card(3, 'D'))
    cards.append(Card(7, 'C'))
    cards.append(Card(4, 'C'))
    cards.append(Card(1, 'H'))
    cards.append(Card(4, 'H'))
    cards.append(Card(5, 'C'))
    cards.append(Card(1, 'S'))
    cards.append(Card(8, 'S'))
    cards.append(Card(1, 'D'))
    cards.append(Card(6, 'S'))
    cards.append(Card(6, 'H'))
    cards.append(Card(1, 'C'))

    cards = Deck().cards[:12]

    hand = Hand(cards)
    print(hand.cards)
    print(hand.sequences)
    hand.add_sequence_increasing_card()
    print(hand.cards)
    print(hand.sequences)
