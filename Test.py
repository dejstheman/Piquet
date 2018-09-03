import itertools
import multiprocessing
import pickle
import random
import sqlite3
from copy import deepcopy
from itertools import combinations

from joblib import Parallel, delayed

import HandStatistics
from Card import Card
from DealState import check_sample_hand
from Deck import Deck
from Hand import Hand, get_longest_sub_sequence


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        create_table(conn)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn):
    points = [0, 4, 5, 6, 7, 8]
    sequences = [0, 3, 4, 15, 16, 17, 18]
    sets = [0, 3, 14]
    sql = '''create table if not exists all_hands_stats
    (point_score integer, sequence_score integer, set_score integer, frequency integer);'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        for p in points:
            for seq in sequences:
                for s in sets:
                    sql = '''insert into all_hands_stats values (?, ?, ?, ?)'''
                    values = (p, seq, s, 0)
                    cursor.execute(sql, values)
    except sqlite3.Error as e:
        print(e)


def update_table(conn, point, seq, set):
    sql = '''update all_hands_stats set frequency = frequency + 1 where point_score = {} and 
    sequence_score = {} and set_score = {}'''.format(point, seq, set)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def record_hand_stat(conn, hand):
    hand = Hand(hand)
    point, seq, set = hand.get_point_value(), hand.get_sequence_value(), hand.get_set_value()
    update_table(conn, point, seq, set)


if __name__ == "__main__":
    conn = create_connection('data/evaluator_stats.db')
    with conn:
        deck = Deck().cards
        for hand in itertools.combinations(deck, 12):
            record_hand_stat(conn, hand)
