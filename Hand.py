from Card import Card
from Deck import Deck
from HandStatistics import compute_point, compute_sequences, compute_sets, compute_best_group


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

    def __repr__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)
