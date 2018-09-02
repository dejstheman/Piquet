import random
import time
from copy import deepcopy

from DealNode import DealNode


def deal_ismcts(root_state, time_resource, exploration=None, result_type="absolute_result", history=False, cheat=False):
    root_node = DealNode() if exploration is None else DealNode(exploration=exploration)
    timeout = time.time() + time_resource
    n = 0
    while time.time() < timeout:
        n += 1
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
    # with open('data/time_resource_simulations.csv', 'a+') as file:
    #     file.write('{},{}\n'.format(time_resource, n))
    return max(root_node.child_nodes, key=lambda child: child.visits).move


def deal_ismcts_decisive(root_state, time_resource, exploration=None,
                         result_type="absolute_result", history=False, cheat=False):
    root_node = DealNode() if exploration is None else DealNode(exploration=exploration)
    timeout = time.time() + time_resource
    while time.time() < timeout:
        node = root_node

        state = root_state.clone_and_randomise(root_state.player_to_play, history, cheat)

        while state.get_decisive_moves() and not node.get_untried_moves(state.get_decisive_moves()):
            node = node.ucb_select_child(state.get_decisive_moves())
            state.do_move(node.move)

        untried_moves = node.get_untried_moves(state.get_decisive_moves())
        if untried_moves:
            move = random.choice(untried_moves)
            player = state.player_to_play
            state.do_move(move)
            node = node.add_child(move, player)

        while state.get_decisive_moves():
            state.do_move(random.choice(state.get_decisive_moves()))

        while node is not None:
            node.update(state, result_type)
            node = node.parent_node

    return max(root_node.child_nodes, key=lambda child: child.visits).move
