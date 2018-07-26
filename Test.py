import random
from copy import deepcopy
from itertools import combinations

import HandStatistics
from Card import Card
from DealState import check_sample_hand
from Deck import Deck
from Hand import Hand, get_longest_sub_sequence


if __name__ == "__main__":
    print(get_longest_sub_sequence([1, 3, 4]))

