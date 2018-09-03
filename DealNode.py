from math import sqrt, log


class DealNode:

    def __init__(self, move=None, parent_node=None, player_just_played=None, exploration=1/sqrt(2)):
        self.move = move
        self.parent_node = parent_node
        self.child_nodes = []
        self.wins = 0
        self.visits = 0
        self.avails = 1
        self.player_just_played = player_just_played
        self.exploration = exploration

    def get_untried_moves(self, legal_moves):
        return [move for move in legal_moves if move not in [child.move for child in self.child_nodes]]

    def ucb_select_child(self, legal_moves):
        legal_children = [child for child in self.child_nodes if child.move in legal_moves]
        for child in legal_children:
            child.avails += 1

        return max(legal_children,
                   key=lambda child: float(child.wins) / float(child.visits) + self.exploration *
                   sqrt(log(child.avails) / float(child.visits)))

    def add_child(self, move, player):
        node = DealNode(move=move, parent_node=self, player_just_played=player)
        self.child_nodes.append(node)
        return node

    def update(self, terminal_state, update_type):
        self.visits += 1
        if self.player_just_played is not None:
            if update_type.startswith('absolute_result'):
                self.wins += terminal_state.get_absolute_result(self.player_just_played)
            elif update_type.startswith('score_strength'):
                self.wins += terminal_state.get_score_strength(self.player_just_played)
            elif update_type.startswith('squashed_result'):
                self.wins += terminal_state.get_squashed_result(self.player_just_played)
            elif update_type.startswith('squashed_score_strength'):
                self.wins += terminal_state.get_squashed_score_strength(self.player_just_played)
