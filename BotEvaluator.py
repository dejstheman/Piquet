import multiprocessing
import random
import sqlite3
import time
from copy import deepcopy
from itertools import combinations
from math import sqrt

from joblib import Parallel, delayed

from DealState import DealState
from DealISMCTS import deal_ismcts
from DealKBS import deal_kbs
from Deck import Deck
from Hand import Hand


def create_partie(players, scores):
    return [DealState(players, scores) if x % 2 == 0 else DealState(players[::-1], scores) for x in range(6)]


def create_sample_games(partie, n):
    return [deepcopy(partie) for _ in range(n)]


def evaluate_bots(bots, db, games, iter_max, explorations):
    db['table_name'] = '{}_vs_{}_bot'.format(bots[0], bots[1])
    scores = {p: 0 for p in bots}
    partie = create_partie(bots, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bots, partie, db, iter_max, explorations)
        for partie in create_sample_games(partie, games))
    conn = create_connection(db['file'])
    with conn:
        create_stats_table(conn, bots)


def bot_partie(bots, partie, db, iter_max, explorations):
    current = deepcopy(partie)
    for deal in current:
        while deal.get_possible_moves():
            if deal.player_to_play == 'kbs':
                deal.do_move(deal_kbs(deal))
            elif deal.player_to_play == 'random':
                deal.do_move(random.choice(deal.get_possible_moves()))
            else:
                e = explorations[bots.index(deal.player_to_play)]
                deal.do_move(deal_ismcts(
                    root_state=deal, iter_max=iter_max, exploration=e, result_type=deal.player_to_play))
    scores = current[0].scores
    values = (iter_max, explorations[0], scores[bots[0]], explorations[1], scores[bots[1]])
    conn = create_connection(db['file'])
    with conn:
        create_table(conn, db['table_name'], bots)
        update_table(conn, db['table_name'], values)


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn, table_name, bots):
    sql = '''create table if not exists {0} (iter_max INTEGER, {1}_exploration REAL, 
{1} INTEGER, {2}_exploration REAL, {2} INTEGER);'''.format(table_name, bots[0], bots[1])
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def update_table(conn, table_name, data):
    sql = '''insert into {} values (?, ?, ?, ?, ?)'''.format(table_name)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
    except sqlite3.Error as e:
        print(e)


def create_stats_table(conn, bots):
    with open('data/get_stats_from_table.txt') as file:
        statements = file.read().format(bots[0], bots[1]).split(';')

    try:
        cursor = conn.cursor()
        for s in statements:
            sql = '''{}'''.format(s.strip())
            cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def create_hands_stats_csv(file):
    with open(file, 'w+') as file:
        file.write('H, S, C, D, point, sequence, set\n')


def update_hand_stats_csv(file, hand):
    hearts = ''.join(sorted([str(card.rank) for card in hand.cards if card.suit == 'H']))
    spades = ''.join(sorted([str(card.rank) for card in hand.cards if card.suit == 'S']))
    clubs = ''.join(sorted([str(card.rank) for card in hand.cards if card.suit == 'C']))
    diamonds = ''.join(sorted([str(card.rank) for card in hand.cards if card.suit == 'D']))
    with open(file, 'a') as file:
        file.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
            hearts, spades, clubs, diamonds, str(hand.get_point_value()),
            str(hand.get_sequence_value()), str(hand.get_set_value())))


def update_hand_stats_csv_in_parallel(conn):
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(update_hand_stats_csv)(conn, Hand(cards))
        for cards in combinations(Deck().cards, 12)
    )


if __name__ == "__main__":
    games = 1
    explorations = [1/sqrt(2)] * 2
    iter_max = 500
    db = {'file': 'data/evaluator_stats.db'}

    bot_names = ['absolute_result', 'score_strength']

    # start = time.time()
    # evaluate_bots(bots=bot_names, db=db, games=games, iter_max=iter_max, explorations=explorations)
    # print(time.time() - start)

    file = 'data/all_possible_hands.csv'
    create_hands_stats_csv(file)
    start = time.time()
    update_hand_stats_csv_in_parallel(file)
    print(time.time() - start)
