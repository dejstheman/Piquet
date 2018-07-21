import multiprocessing
import sqlite3
from copy import deepcopy
from math import sqrt

from joblib import Parallel, delayed

from Deal import Deal
from DealISMCTS import deal_ismcts
from DealKBS import deal_kbs


def create_partie(players, scores):
    return [Deal(players, scores) if x % 2 == 0 else Deal(players[::-1], scores) for x in range(6)]


def create_sample_games(partie, n):
    return [deepcopy(partie) for _ in range(n)]


def evaluate_vs_kbs_bot(bot_name, db, games, time_resource, explorations):
    players = [bot_name, 'kbs']
    db['table_name'] = '{}_vs_kbs_bot'.format(bot_name)
    scores = {p: 0 for p in players}
    partie = create_partie(players, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bot_name, partie, db, time_resource, explorations)
        for partie in create_sample_games(partie, games))


def bot_partie(bot_name, partie, db, time_resource, explorations):
    for e in explorations:
        current = deepcopy(partie)
        for deal in current:
            while deal.get_possible_moves():
                if deal.player_to_play == 'kbs':
                    deal.do_move(deal_kbs(deal))
                else:
                    deal.do_move(deal_ismcts(
                        root_state=deal, time_resource=time_resource, exploration=e, result_type=deal.player_to_play))
        scores = current[0].scores
        values = (time_resource, e, scores[bot_name], scores['kbs'])
        conn = create_connection(db['file'])
        with conn:
            create_table(conn, db['table_name'], bot_name)
            update_table(conn, db['table_name'], values)


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn, table_name, bot_name):
    sql = '''create table if not exists {} (time REAL, exploration REAL, {} INTEGER, kbs INTEGER);'''\
        .format(table_name, bot_name)
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


if __name__ == "__main__":
    games = 250
    time_resource = 0.5
    explorations = [1/sqrt(2)]
    db = {'file': 'data/evaluator_stats.db'}
    bot_name = 'absolute_result'

    evaluate_vs_kbs_bot(bot_name, db, games, time_resource, explorations)
