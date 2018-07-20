from more_itertools import consecutive_groups

from Card import Card


def compute_point(hand):
    point = []
    max_length = max_sum = 0
    for suit in {card.suit for card in hand.cards}:
        cards = [card for card in hand.cards if card.suit == suit]
        if len(cards) >= 4:
            if len(cards) > max_length:
                point = cards
                max_length = len(cards)
                max_sum = sum([card.rank for card in cards])
            elif len(cards) == max_length:
                if sum([card.rank for card in cards]) > max_sum:
                    point = cards
                    max_sum = sum([card.rank for card in cards])
    return point


def compute_sequences(hand):
    sequences = []
    for suit in {card.suit for card in hand.cards}:
        temp = [card.rank for card in hand.cards if card.suit == suit]
        temp.sort()
        for group in consecutive_groups(temp):
            sequence = list(group)
            sequence = [Card(rank, suit) for rank in sequence]
            if len(sequence) >= 4:
                sequences.append(sequence)
    return sequences


def compute_sets(hand):
    sets = {card.rank: [] for card in hand.cards}
    for card in [card for card in hand.cards if card.rank > 3]:
        sets[card.rank].append(card)
    return [card for card in sets.values() if len(card) >= 3]


def compute_best_group(groups):
    max_length = max_rank = 0
    sequence = []
    for seq in groups:
        if len(seq) > max_length:
            sequence = seq
            max_length = len(seq)
            max_rank = max(seq)
        elif len(seq) == max_length:
            if max(seq) > max_rank:
                sequence = seq
    return sequence

