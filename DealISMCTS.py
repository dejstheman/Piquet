import random
import time

from DealNode import DealNode


def deal_ismcts(root_state, time_resource, exploration=None):
    root_node = DealNode() if exploration is None else DealNode(exploration=exploration)
    timeout = time.time() + time_resource

    while True:
        node = root_node

        state = root_state.clone_and_randomise(root_state.player_to_play)

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
            node.update(state)
            node = node.parent_node

        if time.time() > timeout:
            break

    return max(root_node.child_nodes, key=lambda child: child.visits).move
