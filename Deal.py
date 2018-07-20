import random
from copy import deepcopy
from itertools import combinations

from Deck import Deck
from Hand import Hand


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
        self.repique_scored = False
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
        state.repique_scored = self.repique_scored
        state.pique_scored = self.pique_scored
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

    def do_move(self, move):
        if any(x for x in self.carte_blanche.values()) and not self.discards[self.player_to_play]:
            self.carte_blanche_discard(move)
        elif not self.discards[self.player_to_play]:
            self.default_discard(move)
        elif not self.exchanged[self.player_to_play]:
            self.exchange_cards()
        elif not all(self.declarations.values()):
            self.declare_stat(move)
        elif not self.younger_look_up_card and self.players.index(self.player_to_play) == 1:
            self.younger_peep(move)
        elif self.hands[self.player_to_play]:
            self.play_trick(move)

    def carte_blanche_discard(self, move):
        # if elder and carte blanche
        if self.players.index(self.player_to_play) == 0 and self.carte_blanche[self.player_to_play]:
            # choose number of discards only, younger turn
            if not self.no_of_discards[self.player_to_play]:
                self.deal_scores[self.player_to_play] += 10
                self.no_of_discards[self.player_to_play] = move
                self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
                self.player_to_play = self.get_next_player(self.player_to_play)
            # discard cards, show carte blanche
            elif self.discards[self.get_next_player(self.player_to_play)]:
                self.seen_cards[self.get_next_player(self.player_to_play)] += self.hands[self.player_to_play]
                self.discard_cards(move)

        # if younger and carte blanche
        elif self.players.index(self.player_to_play) == 1 and \
                self.carte_blanche[self.get_next_player(self.player_to_play)]:
            # choose number of discards only
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
            # discard cards, show carte blanche
            else:
                self.seen_cards[self.get_next_player(self.player_to_play)] += self.hands[self.player_to_play]
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

        # if elder and younger carte blanche
        elif self.players.index(self.player_to_play) == 0 and \
                self.carte_blanche[self.get_next_player(self.player_to_play)]:
            # choose number of discards
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
                self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
            # discard cards
            else:
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

        # if younger and elder carte blanche
        elif self.players.index(self.player_to_play) == 1 and self.carte_blanche[self.player_to_play]:
            # choose number of discards
            if not self.no_of_discards[self.player_to_play]:
                self.no_of_discards[self.player_to_play] = move
            # discard cards
            else:
                self.discard_cards(move)
                self.player_to_play = self.get_next_player(self.player_to_play)

    def default_discard(self, move):
        if not self.no_of_discards[self.player_to_play]:
            self.no_of_discards[self.player_to_play] = move
            if self.players.index(self.player_to_play) == 0:
                self.max_discards[self.get_next_player(self.player_to_play)] = 8 - move
        else:
            self.discard_cards(move)
            self.player_to_play = self.get_next_player(self.player_to_play)

    def discard_cards(self, discard_cards):
        self.hands[self.player_to_play] = [card for card in self.hands[self.player_to_play]
                                           if card not in discard_cards]
        self.discards[self.player_to_play] = list(discard_cards)

    def exchange_cards(self):
        self.hands[self.player_to_play] += self.talon[:self.no_of_discards[self.player_to_play]]
        self.exchanged[self.player_to_play] = True
        if self.players.index(self.player_to_play) == 0:
            if self.no_of_discards[self.player_to_play] < 5:
                self.seen_cards[self.player_to_play] += self.talon[self.no_of_discards[self.player_to_play]:5]
        self.talon = self.talon[self.no_of_discards[self.player_to_play]:]
        if len(self.talon) == 0:
            self.younger_look_up_card = True
        self.player_to_play = self.get_next_player(self.player_to_play)

    def declare_stat(self, move):
        if move == 'point':
            self.declare_point()
        elif move == 'sequence':
            self.declare_sequence()
        elif move == 'set':
            self.declare_set()
        else:
            if not self.declarations['point']:
                self.declarations['point'] = True
            elif not self.declarations['sequence']:
                self.declarations['sequence'] = True
            else:
                self.declarations['set'] = True

    def declare_point(self):
        elder = Hand(self.hands[self.player_to_play])
        younger = Hand(self.hands[self.get_next_player(self.player_to_play)])

        self.compare_declarations('point', elder.get_point_value(), elder.get_point_sum(),
                                  younger.get_point_value(), younger.get_point_sum())
        self.deal_scores[self.player_to_play] += self.declaration_values[self.player_to_play]['point']

    def declare_sequence(self):
        elder = Hand(self.hands[self.player_to_play])
        younger = Hand(self.hands[self.get_next_player(self.player_to_play)])

        self.compare_declarations('sequence', elder.get_sequence_value(), elder.get_sequence_rank(),
                                  younger.get_sequence_value(), younger.get_sequence_rank())
        self.deal_scores[self.player_to_play] += self.declaration_values[self.player_to_play]['sequence']
        self.check_for_repique()

    def declare_set(self):
        elder = Hand(self.hands[self.player_to_play])
        younger = Hand(self.hands[self.get_next_player(self.player_to_play)])

        self.compare_declarations('set', elder.get_set_value(), elder.get_set_rank(),
                                  younger.get_set_value(), younger.get_set_rank())
        self.deal_scores[self.player_to_play] += self.declaration_values[self.player_to_play]['set']
        self.check_for_repique()

    def compare_declarations(self, stat, elder_value, elder_rank, younger_value, younger_rank):
        if elder_value > younger_value:
            self.declaration_values[self.player_to_play][stat] = elder_value
        elif elder_value == younger_value:
            if elder_rank > younger_rank:
                self.declaration_values[self.player_to_play][stat] = elder_value
            elif younger_rank > elder_rank:
                self.declaration_values[self.get_next_player(self.player_to_play)][stat] = younger_value
        else:
            self.declaration_values[self.get_next_player(self.player_to_play)][stat] = younger_value
        self.declarations[stat] = True

    def update_deal_score(self, player, score):
        self.deal_scores[player] += score
        if not self.repique_scored and not self.pique_scored:
            self.check_for_pique(player)

    def check_for_repique(self):
        for p in self.players:
            player_declarations = sum(self.declaration_values[p].values())
            opponent_declarations = sum(self.declaration_values[self.get_next_player(p)].values())
            if ((player_declarations >= 20 and self.carte_blanche[p]) or player_declarations >= 30) and \
                    opponent_declarations == 0 and not self.repique_scored:
                self.deal_scores[p] += 60
                self.repique_scored = True

    def check_for_pique(self, player):
        if self.deal_scores[player] >= 30 and \
                self.deal_scores[self.get_next_player(player)] == 0:
            self.deal_scores[player] += 30
            self.pique_scored = True

    def younger_peep(self, move):
        if move == 'peep':
            for p in self.players:
                self.seen_cards[p] += self.talon
        self.younger_look_up_card = True

    def play_trick(self, move):
        if self.tricks_in_round == 12 and self.players.index(self.player_to_play) == 1:
            if self.carte_blanche[self.player_to_play]:
                self.update_deal_score(self.player_to_play, 10)
            self.update_deal_score(self.player_to_play, sum(self.declaration_values[self.player_to_play].values()))

        if not self.current_trick:
            self.update_deal_score(self.player_to_play, 1)
        self.current_trick.append((self.player_to_play, move))
        self.hands[self.player_to_play].remove(move)
        self.player_to_play = self.get_next_player(self.player_to_play)

        if any(True for player, _ in self.current_trick if player == self.player_to_play):
            self.compute_trick_winner()

    def compute_trick_winner(self):
        self.tricks_in_round -= 1
        _, lead_card = self.current_trick[0]

        sorted_plays = sorted([(player, card.rank) for (player, card) in self.current_trick
                               if card.suit == lead_card.suit], key=lambda trick: trick[1], reverse=True)

        trick_winner = sorted_plays[0][0]
        self.tricks_won[trick_winner] += 1

        if self.tricks_in_round == 0:
            self.update_deal_score(trick_winner, 2)

            if len(set(self.tricks_won.values())) > 1:
                max_trick_winner = max(self.players, key=lambda p: self.tricks_won[p])
                self.deal_scores[max_trick_winner] += 10
                if self.tricks_won[max_trick_winner] == 12:
                    self.deal_scores[max_trick_winner] += 40

            for p in self.players:
                self.scores[p] += self.deal_scores[p]
        else:
            self.update_deal_score(trick_winner, 1)

        for p in self.players:
            self.seen_cards[p] += [card for _, card in self.current_trick]
        self.current_trick = []
        self.player_to_play = trick_winner

    def get_possible_moves(self):
        if not self.no_of_discards[self.player_to_play]:
            return self.get_possible_no_of_discards()
        elif not self.discards[self.player_to_play]:
            return self.get_possible_discards()
        elif not self.exchanged[self.player_to_play]:
            return ['exchange']
        elif not all(self.declarations.values()):
            return self.get_possible_declarations()
        elif not self.younger_look_up_card and self.players.index(self.player_to_play) == 1:
            return ['peep', 'pass']
        else:
            return self.get_possible_tricks()

    def get_possible_no_of_discards(self):
        return range(3, self.max_discards[self.player_to_play] + 1)

    def get_possible_discards(self):
        return list(combinations(Hand(self.hands[self.player_to_play]).get_discard_cards(7),
                                 self.no_of_discards[self.player_to_play]))

    def get_possible_declarations(self):
        if self.players.index(self.player_to_play) == 0:
            if not self.declarations['point']:
                return ['point', 'pass']
            elif not self.declarations['sequence']:
                return ['sequence', 'pass']
            elif not self.declarations['set']:
                return ['set', 'pass']

    def get_possible_tricks(self):
        if not self.current_trick:
            return self.hands[self.player_to_play]
        else:
            _, lead_card = self.current_trick[0]
            cards_in_suit = [card for card in self.hands[self.player_to_play] if card.suit == lead_card.suit]
            if cards_in_suit:
                return cards_in_suit
            else:
                return self.hands[self.player_to_play]

    def get_result(self, player):
        return 0 if self.deal_scores[player] <= self.deal_scores[self.get_next_player(player)] else 1

    def __repr__(self):
        result = ""
        for p in self.players:
            # hand = Hand(self.hands[p])
            # result += "\n{} hand: {}\n".format(p, self.hands[p])
            # result += "{} carte blanche: {}\n".format(p, self.carte_blanche[p])
            # result += "{} discards: {}\n".format(p, self.discards[p])
            # result += "{} seen cards: {}\n".format(p, self.seen_cards[p])
            # result += "{} point: {} sequence: {} set: {}\n".format(
            #     p, hand.points, hand.get_best_sequence(), hand.get_best_set())
            result += "{} score: {}\n".format(p, self.scores[p])

        return result


if __name__ == "__main__":
    players = ['ai', 'human']
    scores = {p: 0 for p in players}

    deal = Deal(players, scores)

    while deal.get_possible_moves():
        deal.do_move(deal.get_possible_moves()[0])

    print(deal)
