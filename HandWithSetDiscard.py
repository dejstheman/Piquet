from Hand import Hand


class HandWithSetDiscard(Hand):

    def __init__(self, cards):
        super().__init__(cards)

    def get_discard_cards(self, n, hand_type):
        high_cards = [card for card in self.cards if card.rank in range(6, 8)] if hand_type == 'younger' \
            else [card for card in self.cards if card.rank == 8]
        set_point = sorted([card for card in self.get_best_set() if card in self.points])
        set_point_seq = sorted([card for card in self.get_best_set() if card not in set_point])
        set_point_seq_high_cards = sorted(
            [card for card in self.get_best_set()
             if any(True for c in high_cards if c.suit == card.suit) and card not in set_point + set_point_seq])
        set_cards = sorted([card for card in self.get_best_set()
                            if card not in set_point + set_point_seq + set_point_seq_high_cards])
        remaining_cards = sorted([card for card in self.cards if
                                  card not in set_point_seq_high_cards + set_point_seq + set_point + set_cards])

        untouchables = []

        while len(untouchables) != n:
            if set_point_seq_high_cards:
                untouchables.append(set_point_seq_high_cards.pop(-1))
            elif set_point_seq:
                untouchables.append(set_point_seq.pop(-1))
            elif set_point:
                untouchables.append(set_point.pop(-1))
            elif set_cards:
                untouchables.append(set_cards.pop(-1))
            else:
                untouchables.append(remaining_cards.pop(-1))

        return [card for card in self.cards if card not in untouchables]
