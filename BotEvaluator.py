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


def evaluate_vs_bot(bots, db, games, time_resource, explorations):
    db['table_name'] = '{}_vs_{}_bot'.format(bots[0], bots[1])
    scores = {p: 0 for p in bots}
    partie = create_partie(bots, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bots, partie, db, time_resource, explorations)
        for partie in create_sample_games(partie, games))
    conn = create_connection(db['file'])
    with conn:
        create_stats_table(conn, bots)


def bot_partie(bots, partie, db, time_resource, explorations):
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
        values = (time_resource, e, scores[bots[0]], scores[bots[1]])
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
    sql = '''create table if not exists {} (time REAL, exploration REAL, {} INTEGER, {} INTEGER);'''\
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
    games = 150
    time_resource = 0.5
    explorations = [0.1, 0.2, 0.3]
    db = {'file': 'data/evaluator_stats.db'}
    bot_names = ['score_strength', 'kbs']
    # bot_names = ['absolute_result', 'score_strength']

    # for bot in bot_names:
    #     evaluate_vs_kbs_bot(bot, db, games, time_resource, explorations)

    evaluate_vs_bot(bot_names, db, games, time_resource, explorations)
