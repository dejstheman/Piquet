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

    def remove_cards(self, card):
        self.cards.remove(card)

    def add_card(self, card):
        self.cards.append(card)
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

    def get_point_increasing_cards(self, possible_cards):
        suit_points = {card.suit: len([c for c in self.cards if c.suit == card.suit]) for card in self.cards}
        point_sorted_suit = [p[0] for p in sorted(suit_points.items(), key=lambda x: x[1], reverse=True)]
        result = []
        for suit in point_sorted_suit:
            for card in [c for c in possible_cards if c.suit == suit]:
                temp = Hand(deepcopy(self.cards))
                temp.cards.append(card)
                if temp.get_sequence_value() == self.get_sequence_value() \
                        and temp.get_set_value() == self.get_set_value():
                    result.append(card)

        return result

    def get_sequence_increasing_cards(self, possible_cards):
        suit_seqs = {suit: max([list(g)
                                for g in consecutive_groups(
                sorted([card.rank for card in hand.cards if card.suit == suit]))],
                               key=lambda g: len(g)) for suit in {card.suit for card in self.cards}}
        seq_sorted_suits = [p[0] for p in sorted(suit_seqs.items(), key=lambda x: len(x[1]), reverse=True)]

        result = []
        for suit in seq_sorted_suits:
            suit_cards = sorted([card.rank for card in self.cards if card.suit == suit])
            missing = sorted(set(range(1, 9)).difference(suit_cards))
            sub_seqs = {}
            for c in missing:
                temp = deepcopy(suit_cards)
                temp.append(c)
                sub_seqs[c] = get_longest_sub_sequence(sorted(temp))
            sub_seqs_sorted = [p[0] for p in sorted(sub_seqs.items(), key=lambda x: (x[1], x[0]), reverse=True)]
            for rank in sub_seqs_sorted:
                for card in [card for card in possible_cards if card.suit == suit]:
                    if card.rank == rank:
                        temp = Hand(deepcopy(self.cards))
                        temp.cards.append(card)
                        if temp.get_point_value() == self.get_point_value() and \
                                temp.get_set_value() == self.get_set_value():
                            result.append(card)

        return result

    def get_set_increasing_cards(self, possible_cards):
        rank_sets = {rank: len([card for card in self.cards if card.rank == rank])
                     for rank in {card.rank for card in self.cards if card.rank in range(4, 9)}}
        set_sorted_ranks = [p[0] for p in sorted(rank_sets.items(), key=lambda x: (x[1], x[0]), reverse=True)]
        result = []
        for rank in set_sorted_ranks:
            for card in [card for card in possible_cards if card.rank == rank]:
                temp = Hand(deepcopy(self.cards))
                temp.cards.append(card)
                if temp.get_point_value() == self.get_point_value() and \
                        temp.get_sequence_value() == self.get_sequence_value():
                    result.append(card)

        return result

    def get_impotent_card(self, possible_cards):
        impotent_cards = []
        for card in possible_cards:
            temp = Hand(deepcopy(self.cards))
            temp.cards.append(card)
            if temp.get_point_value() == self.get_point_value() \
                    and temp.get_sequence_value() == self.get_sequence_value() \
                    and temp.get_set_value() == self.get_set_value():
                impotent_cards.append(card)
        return impotent_cards if impotent_cards else possible_cards

    def add_random_card(self, stat_target, possible_cards):
        addable_cards = deepcopy(possible_cards)
        if stat_target['point']:
            addable_cards = [
                card for card in addable_cards if card in self.get_point_increasing_cards(addable_cards)]
        if stat_target['sequence']:
            addable_cards = [
                card for card in addable_cards if card in self.get_sequence_increasing_cards(addable_cards)]
        if stat_target['set']:
            addable_cards = [
                card for card in addable_cards if card in self.get_set_increasing_cards(addable_cards)]
        if not any(stat_target.values()):
            self.add_card(random.choice(self.get_impotent_card(possible_cards)))
        else:
            if not addable_cards:
                self.add_card(random.choice(self.get_impotent_card(possible_cards)))
            else:
                self.add_card(addable_cards[0])

    def __repr__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)


if __name__ == "__main__":
    cards = []
    cards.append(Card(3, 'D'))
    cards.append(Card(3, 'S'))
    cards.append(Card(1, 'C'))
    cards.append(Card(1, 'H'))
    cards.append(Card(4, 'H'))
    cards.append(Card(5, 'C'))
    cards.append(Card(1, 'S'))
    cards.append(Card(8, 'S'))
    cards.append(Card(1, 'D'))
    cards.append(Card(6, 'S'))
    cards.append(Card(6, 'H'))
    cards.append(Card(1, 'C'))

    cards = Deck().cards[:0]

    hand = Hand(cards)
    target = {'point': 5, 'sequence': 0, 'set': 3}

    while len(hand.cards) < 12:
        stats = {'point': hand.get_point_value() != target['point'] if target['point'] > 0 else False,
                 'sequence': hand.get_sequence_value() != target['sequence'] if target['sequence'] > 0 else False,
                 'set': hand.get_set_value() != target['set'] if target['set'] > 0 else False}
        hand.add_random_card(stats, hand.get_remaining_cards())
        if (hand.get_point_value() > target['point'] and stats['point']) or \
                (hand.get_set_value() > target['set'] and stats['set']) or \
                (hand.get_sequence_value() > target['sequence'] and stats['sequence']):
            cards = [card for card in hand.points + hand.get_best_set() + hand.get_best_sequence() if card not in cards]
            if cards:
                hand.remove_cards(random.choice(cards))
            else:
                hand.remove_cards(random.choice(hand.cards))

    print('point: ', hand.get_point_value())
    print('sequence: ', hand.get_sequence_value())
    print('set: ', hand.get_set_value())
    print(len(hand.cards))
