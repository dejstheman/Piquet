import random
from copy import deepcopy

from Deck import Deck


class Deal:

    def __init__(self, players, scores):
        self.players = players
        self.player_to_play = self.players[0]
        self.scores = scores
        self.deal_scores = {p: 0 for p in self.players}
        deck = Deck()
        self.hands = {p: deck.cards[12 * self.players.index(p):12 * (self.players.index(p) + 1)] for p in self.players}
        self.talon = [card for card in deck.cards if card not in [x for hand in self.hands.values() for x in hand]]
        self.carte_blanche = {p: all(x not in {card.rank for card in self.hands[p]}
                                     for x in range(5, 8)) for p in self.players}
        self.max_discards = {self.players[0]: 5, self.players[1]: 3}
        self.no_of_discards = {p: 0 for p in self.players}
        self.discards = {p: [] for p in self.players}
        self.seen_cards = {p: [] for p in self.players}
        self.exchanged = {p: False for p in self.players}
        self.younger_look_up_card = False
        self.declarations = {'point': False, 'sequence': False, 'set': False}
        self.declaration_values = {p: {'point': 0, 'sequence': 0, 'set': 0} for p in self.players}
        self.repique_scored = {p: False for p in self.players}
        self.pique_scored = False
        self.current_trick = []
        self.max_tricks = 12
        self.tricks_in_round = 12
        self.tricks_won = {p: 0 for p in self.players}

    def clone(self):
        state = Deal(deepcopy(self.players), deepcopy(self.scores))
        state.player_to_play = self.player_to_play
        state.deal_scores = deepcopy(self.deal_scores)
        state.hands = deepcopy(self.hands)
        state.talon = deepcopy(self.talon)
        state.carte_blanche = deepcopy(self.carte_blanche)
        state.max_discards = deepcopy(self.max_discards)
        state.no_of_discards = deepcopy(self.no_of_discards)
        state.discards = deepcopy(self.discards)
        state.seen_cards = deepcopy(self.seen_cards)
        state.exchanged = deepcopy(self.exchanged)
        state.younger_look_up_card = self.younger_look_up_card
        state.declarations = deepcopy(self.declarations)
        state.declaration_values = deepcopy(self.declaration_values)
        state.repique_scored = deepcopy(self.repique_scored)
        state.current_trick = deepcopy(self.current_trick)
        state.tricks_in_round = self.tricks_in_round
        state.tricks_in_round = deepcopy(self.tricks_in_round)

        return state

    def clone_and_randomise(self, observer):
        state = self.clone()

        seen_cards = state.hands[observer] + state.seen_cards[observer] + state.discards[observer] + \
                     [card for _, card in state.current_trick]

        unseen_cards = [card for card in Deck().cards if card not in seen_cards]
        random.shuffle(unseen_cards)

        if not self.exchanged[observer] or not self.exchanged[self.get_next_player(observer)]:
            talon_length = len(self.talon)
            state.talon = unseen_cards[:talon_length]
            unseen_cards = unseen_cards[talon_length:]

        seen_cards_length = len(self.seen_cards[self.get_next_player(observer)])
        discards_length = len(self.discards[self.get_next_player(observer)]) + seen_cards_length
        hand_length = len(self.hands[self.get_next_player(observer)]) + discards_length

        state.seen_cards[self.get_next_player(observer)] = unseen_cards[:seen_cards_length]
        state.discards[self.get_next_player(observer)] = unseen_cards[seen_cards_length:discards_length]
        state.hands[self.get_next_player(observer)] = unseen_cards[discards_length:hand_length]

        return state

    def get_next_player(self, player):
        return [p for p in self.players if p != player][0]

    def carte_blanche_discard(self, move):
        # if elder and carte blanche
        if self.players.index(self.player_to_play) == 0 and self.carte_blanche[self.player_to_play]:
            # choose number of discards, but do not discard yet
            if not self.no_of_discards[self.player_to_play]:
                self.deal_scores[self.player_to_play] += 10
                self.no_of_discards[self.player_to_play] = move
                self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
                self.player_to_play = self.get_next_player(self.player_to_play)
            # discard cards
            elif self.discards[self.get_next_player(self.player_to_play)]:
                self.seen_cards[self.get_next_player(self.player_to_play)] += self.hands[self.player_to_play]
                self.discard_cards(move)

        #
        elif self.players.index(self.player_to_play) == 1 and self.carte_blanche[self.get_next_player(self.player_to_play)]:
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
            else:
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

        elif self.players.index(self.player_to_play) == 0 and self.carte_blanche[self.get_next_player(self.player_to_play)]:
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
                self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
            else:
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

        elif self.players.index(self.player_to_play) == 1 and self.carte_blanche[self.player_to_play]:
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
            else:
                self.seen_cards[self.get_next_player(self.player_to_play)] += self.hands[self.player_to_play]
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

    def default_discard(self, move):
        if not self.no_of_discards[self.player_to_play]:
            self.no_of_discards[self.player_to_play] = move
            self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
        else:
            self.discard_cards(move)
            self.player_to_play = self.get_next_player(self.player_to_play)

    def discard_cards(self, discard_cards):
        self.hands[self.player_to_play] = [card for card in self.hands[self.player_to_play]
                                           if card not in discard_cards]
        self.discards[self.player_to_play] = list(discard_cards)

