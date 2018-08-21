import random
from copy import deepcopy

from DealNode import DealNode


def deal_ismcts(root_state, iter_max, exploration=None, result_type="absolute_result", history=False, cheat=False):
    root_node = DealNode() if exploration is None else DealNode(exploration=exploration)

    for i in range(iter_max):
        node = root_node

        state = root_state.clone_and_randomise(root_state.player_to_play, history, cheat)

        while state.get_possible_moves() and not node.get_untried_moves(state.get_possible_moves()):
            node = node.ucb_select_child(state.get_possible_moves())
            state.do_move(node.move)

        untried_moves = node.get_untried_moves(state.get_possible_moves())
        if untried_moves:
            move = random.choice(untried_moves)
            player = state.player_to_play
            state.do_move(move)
            node = node.add_child(move, player)

        while state.get_possible_moves():
            state.do_move(random.choice(state.get_possible_moves()))

        while node is not None:
            node.update(state, result_type)
            node = node.parent_node

    return max(root_node.child_nodes, key=lambda child: child.visits).move
