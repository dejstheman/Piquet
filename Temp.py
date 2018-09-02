from Deck import Deck
from Hand import Hand


def get_needed_cards(hand):
    remaining_named_cards = [card for card in Deck().cards if card not in hand.cards if card.rank > 3]
    point_count = {s: len([card for card in hand.cards if card.suit == s]) for s in {card.suit for card in hand.cards}}
    set_count = {r: len([card for card in hand.cards if card.rank == r])
                 for r in {card.rank for card in hand.cards if card.rank > 3}}
    print(set_count)


if __name__ == '__main__':
    get_needed_cards(Hand(Deck().cards[:12]))
