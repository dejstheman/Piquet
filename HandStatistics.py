from more_itertools import consecutive_groups

from Card import Card


def compute_point(hand):
    point = []
    max_length = 0
    max_sum = 0
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


def compute_opponent_maximum_point(hand, suit=None):
    remaining_cards = hand.get_remaining_cards()
    points = {s: len([card for card in remaining_cards if card.suit == s])
              for s in {card.suit for card in remaining_cards}}
    print(points)
    return points[max(points, key=points.get)] if suit is None else points[suit]


def compute_sequences(hand):
    sequences = []
    for suit in {card.suit for card in hand.cards}:
        temp = sorted([card.rank for card in hand.cards if card.suit == suit])
        for group in consecutive_groups(temp):
            sequence = [Card(rank, suit) for rank in list(group)]
            if len(sequence) >= 4:
                sequences.append(sequence)
    return sequences


def compute_opponent_maximum_sequence(hand, suit=None):
    remaining_cards = hand.get_remaining_cards()
    sequences = {card.suit: [] for card in remaining_cards}
    max_sequence = []
    for s in sequences:
        ranks = sorted([card.rank for card in remaining_cards if card.suit == s])
        temp = []
        for group in consecutive_groups(ranks):
            sequence = [Card(rank, s) for rank in list(group)]
            temp.append(sequence)
            sequences[s] = sequence \
                if len(sequence) > len(sequences[s]) \
                or (len(sequence) == len(sequences[s]) and sum([card.rank for card in sequence]) >
                    sum([card.rank for card in sequences[s]])) else sequences[s]
        if len(sequences[s]) > len(max_sequence):
            max_sequence = sequences[s]
        elif len(sequences[s]) == len(max_sequence):
            max_sequence = sequences[s] if max(sequences[s]) > max(max_sequence) else max_sequence
    return max_sequence if suit is None else sequences[suit]


def compute_sets(hand):
    sets = {card.rank: [] for card in hand.cards}
    for card in [card for card in hand.cards if card.rank > 3]:
        sets[card.rank].append(card)
    return [card for card in sets.values() if len(card) >= 3]


def compute_opponent_maximum_set(hand, rank=None):
    remaining_cards = hand.get_remaining_cards()
    sets = {card.rank: [] for card in remaining_cards if card.rank > 3}
    max_set = []
    for card in [card for card in remaining_cards if card.rank > 3]:
        sets[card.rank].append(card)
    for r in sets:
        if len(sets[r]) > len(max_set):
            max_set = sets[r]
        elif len(sets[r]) == len(max_set):
            max_set = sets[r] if r > max(max_set).rank else max_set
    return max_set if rank is None else sets[rank]


def compute_best_group(groups):
    max_length = 0
    max_rank = 0
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
