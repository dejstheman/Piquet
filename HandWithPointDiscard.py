from Hand import Hand


class HandWithPointDiscard(Hand):

    def __init__(self, cards):
        super().__init__(cards)

    def get_discard_cards(self, n, hand_type):
        high_cards = [card for card in self.cards if card.rank in range(6, 8)] if hand_type == 'younger' \
            else [card for card in self.cards if card.rank == 8]
        point_set = sorted([card for card in self.points if card in self.get_best_set()])
        point_set_seq = sorted(
            [card for card in self.points if card in self.get_best_sequence() and card not in point_set])
        point_set_seq_aces = sorted(
            [card for card in self.points if any(True for c in high_cards if c.suit == card.suit)
             and card not in point_set + point_set_seq])
        point = sorted([card for card in self.points if card not in point_set + point_set_seq + point_set_seq_aces])
        remaining_cards = sorted([card for card in self.cards if
                                  card not in point_set + point_set_seq + point_set_seq_aces + point])
        untouchables = []

        while len(untouchables) != n:
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

        return [card for card in self.cards if card not in untouchables]
