import multiprocessing
import random
import sqlite3
import time
from copy import deepcopy
from math import sqrt

from joblib import Parallel, delayed

from DealState import DealState
from DealISMCTS import deal_ismcts
from DealKBS import deal_kbs


def create_partie(players, scores):
    return [DealState(players, scores) if x % 2 == 0 else DealState(players[::-1], scores) for x in range(6)]


def create_sample_games(partie, n):
    return [deepcopy(partie) for _ in range(n)]


def evaluate_bots(bots, discard_strategies, histories, db, games, iter_max, explorations):
    db['table_name'] = '{}_vs_{}_bot'.format(bots[0], bots[1])
    scores = {p: 0 for p in bots}
    partie = create_partie(bots, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bots, discard_strategies, histories, partie, db, iter_max, explorations)
        for partie in create_sample_games(partie, games))
    conn = create_connection(db['file'])
    with conn:
        create_stats_table(conn, bots)


def bot_partie(bots, discard_strategies, histories, partie, db, iter_max, explorations):
    for e in explorations:
        current = deepcopy(partie)
        for deal in current:
            while deal.get_possible_moves():
                if deal.player_to_play == 'kbs':
                    deal.do_move(deal_kbs(deal))
                elif deal.player_to_play == 'random':
                    deal.do_move(random.choice(deal.get_possible_moves()))
                else:
                    discard = discard_strategies[bots.index(deal.player_to_play)]
                    history = histories[bots.index(deal.player_to_play)]
                    deal.do_move(deal_ismcts(
                        root_state=deal, iter_max=iter_max, exploration=e, result_type=deal.player_to_play,
                        discard_strategy=discard, history=history))
        scores = current[0].scores
        values = (iter_max, e, scores[bots[0]], scores[bots[1]])
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
    sql = '''create table if not exists {} (iter_max INTEGER, exploration REAL, {} INTEGER, {} INTEGER);'''\
        .format(table_name, bots[0], bots[1])
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def update_table(conn, table_name, data):
    sql = '''insert into {} values (?, ?, ?, ?)'''.format(table_name)
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


if __name__ == "__main__":
    games = 100
    explorations = [1/sqrt(2)]
    iter_max = 500
    db = {'file': 'data/evaluator_stats.db'}

    bot_names = []
    bot_names.append(['rubicon_result_point', 'absolute_result_greedy'])
    bot_names.append(['rubicon_result_point', 'absolute_result_set'])
    bot_names.append(['rubicon_result_point', 'absolute_result_point'])
    bot_names.append(['rubicon_result_set', 'absolute_result_greedy'])
    bot_names.append(['rubicon_result_set', 'absolute_result_set'])
    bot_names.append(['rubicon_result_set', 'absolute_result_point'])
    bot_names.append(['rubicon_result_set', 'rubicon_result_point'])
    discard_strategies = []
    discard_strategies.append(['point', 'greedy'])
    discard_strategies.append(['point', 'set'])
    discard_strategies.append(['point', 'point'])
    discard_strategies.append(['set', 'greedy'])
    discard_strategies.append(['set', 'set'])
    discard_strategies.append(['set', 'point'])
    discard_strategies.append(['set', 'point'])
    histories = [[False, False]] * 7

    for i in range(len(bot_names)):
        evaluate_bots(bot_names[i], discard_strategies[i], histories[i], db, games, iter_max, explorations)
        # print(bot_names[i], discard_strategies[i], histories[i])
