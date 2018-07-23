import random
import time
from copy import deepcopy

from DealISMCTS import deal_ismcts
from DealKBS import deal_kbs
from DealState import DealState
from Deck import Deck
from Hand import Hand


class DealStateWithHistory(DealState):

    def __init__(self, players, scores, history):
        super().__init__(players, scores, history)
        self.opponent_cards = {p: [] for p in self.players}

    def clone(self):
        state = DealStateWithHistory(deepcopy(self.players), deepcopy(self.scores))
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
        state.public_cards = deepcopy(self.public_cards)
        state.tricks_in_round = self.tricks_in_round
        state.tricks_in_round = deepcopy(self.tricks_in_round)
        state.opponent_cards = deepcopy(self.opponent_cards)

        return state

    def clone_and_randomise(self, observer):
        state = self.clone()

        seen_cards = state.hands[observer] + state.seen_cards[observer] + state.discards[
            observer] + state.public_cards + state.opponent_cards[observer] + [card for _, card in state.current_trick]

        unseen_cards = [card for card in Deck().cards if card not in seen_cards]

        hand_length = len(state.hands[state.get_next_player(observer)])
        opponent = state.get_next_player(observer)

        if state.declarations['point'] and not state.declarations['sequence'] and not state.declarations['set']:
            while True:
                temp = random.sample(unseen_cards, hand_length)
                hand = Hand(state.opponent_cards[observer] + temp)
                target = [state.declaration_values[opponent]['point']]
                sample = [hand.get_point_value()]
                if state.check_sample_hand(target, sample):
                    unseen_cards = state.remove_hand_from_unseen(player=opponent, hand=temp, unseen_cards=unseen_cards)
                    break
        elif state.declarations['point'] and state.declarations['sequence'] and not state.declarations['set']:
            while True:
                temp = random.sample(unseen_cards, hand_length)
                hand = Hand(state.opponent_cards[observer] + temp)
                stats = ['point', 'sequence']
                target = [state.declaration_values[opponent][stat] for stat in stats]
                sample = [hand.get_point_value(), hand.get_sequence_value()]
                if state.check_sample_hand(target, sample):
                    unseen_cards = state.remove_hand_from_unseen(player=opponent, hand=temp, unseen_cards=unseen_cards)
                    break
        elif state.declarations['point'] and state.declarations['sequence'] and state.declarations['set']:
            while True:
                temp = random.sample(unseen_cards, hand_length)
                hand = Hand(state.opponent_cards[observer] + temp)
                stats = ['point', 'sequence', 'set']
                target = [state.declaration_values[opponent][stat] for stat in stats]
                sample = [hand.get_point_value(), hand.get_sequence_value(), hand.get_set_value()]
                if state.check_sample_hand(target, sample):
                    unseen_cards = state.remove_hand_from_unseen(player=opponent, hand=temp, unseen_cards=unseen_cards)
                    break
        else:
            state.hands[opponent] = unseen_cards[:hand_length]
            unseen_cards = unseen_cards[hand_length:]

        if not state.exchanged[observer] or not state.exchanged[opponent]:
            talon_length = len(state.talon)
            state.talon = unseen_cards[:talon_length]
            unseen_cards = [card for card in unseen_cards if card not in state.talon]

        seen_cards_length = len(state.seen_cards[opponent])
        discards_length = len(state.discards[opponent]) + seen_cards_length

        state.seen_cards[opponent] = unseen_cards[:seen_cards_length]
        state.discards[opponent] = unseen_cards[seen_cards_length:discards_length]

        return state

    # noinspection PyMethodMayBeStatic
    def check_sample_hand(self, target, sample):
        return all(j == i for i, j in list(zip(target, sample)) if i > 0)

    def remove_hand_from_unseen(self, player, hand, unseen_cards):
        self.hands[player] = hand
        return [card for card in unseen_cards if card not in hand]

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

        self.public_cards += [card for _, card in self.current_trick]
        for p in self.players:
            self.opponent_cards[p] += \
                [card for player, card in self.current_trick if player == self.get_next_player(p)]
        self.current_trick = []
        self.player_to_play = trick_winner


if __name__ == "__main__":
    players = ['absolute_result', 'human']
    scores = {p: 0 for p in players}

    deal = DealStateWithHistory(players, scores)

    start = time.time()
    while deal.get_possible_moves():
        if deal.player_to_play == 'absolute_result':
            deal.do_move(deal_ismcts(deal, 1, result_type=deal.player_to_play, discard_strategy='set'))
        else:
            deal.do_move(deal_kbs(deal))
    print(time.time() - start)

    print(deal)
