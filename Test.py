import random
from copy import deepcopy
from itertools import combinations

import HandStatistics
from Card import Card
from DealState import check_sample_hand
from Deck import Deck
from Hand import Hand, get_longest_sub_sequence


if __name__ == "__main__":
    test = 'kbs_vs_random_partie_bots'
    print(test.replace('partie', 'deal'))
    print(test)
