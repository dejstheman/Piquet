import multiprocessing
import random
import sqlite3
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


def evaluate_bots_parallel(bots, db, games, iter_max, explorations, histories):
    db['table_name'] = '{}_vs_{}_partie_bots'.format(bots[0], bots[1])
    scores = {p: 0 for p in bots}
    partie = create_partie(bots, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bots, partie, db, iter_max, explorations, histories)
        for partie in create_sample_games(partie, games))
    conn = create_connection(db['file'])
    with conn:
        create_stats_table(conn, bots, 'data/get_partie_stats_from_table.txt')
        create_stats_table(conn, bots, 'data/get_deal_stats_from_table.txt')


def bot_partie(bots, partie, db, iter_max, explorations, histories):
    conn = create_connection(db['file'])
    current = deepcopy(partie)
    for deal in current:
        e = explorations[bots.index(deal.player_to_play)]
        while deal.get_possible_moves():
            if deal.player_to_play == 'kbs':
                deal.do_move(deal_kbs(deal))
            elif deal.player_to_play == 'random':
                deal.do_move(random.choice(deal.get_possible_moves()))
            elif deal.player_to_play == 'cheat':
                deal.do_move(deal_ismcts(
                    root_state=deal, time_resource=iter_max, exploration=e, result_type='absolute_result',
                    history=histories[deal.players.index(deal.player_to_play)], cheat=True))
            else:
                deal.do_move(deal_ismcts(
                    root_state=deal, time_resource=iter_max, exploration=e, result_type=deal.player_to_play,
                    history=histories[deal.players.index(deal.player_to_play)]))
        scores = deal.deal_scores
        values = (iter_max, explorations[0], scores[bots[0]], explorations[1], scores[bots[1]],
                  deal.repique, deal.pique, deal.cards, deal.capot)
        with conn:
            table_name = db['table_name'].replace('partie', 'deal')
            create_table(conn, table_name, bots, True)
            update_table(conn, table_name, values, True)
    scores = current[0].scores
    values = (iter_max, explorations[0], scores[bots[0]], explorations[1], scores[bots[1]])
    with conn:
        create_table(conn, db['table_name'], bots, False)
        update_table(conn, db['table_name'], values, False)


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn, table_name, bots, deal):
    sql = '''create table if not exists {0} (iter_max INTEGER, {1}_exploration REAL, {1} INTEGER, {2}_exploration REAL, 
    {2} INTEGER, repique TEXT, pique TEXT, cards TEXT, capot TEXT);'''.format(table_name, bots[0], bots[1]) \
        if deal else '''create table if not exists {0} (iter_max INTEGER, {1}_exploration REAL, {1} INTEGER, {2}_exploration REAL, 
    {2} INTEGER);'''.format(table_name, bots[0], bots[1])
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def update_table(conn, table_name, data, deal):
    sql = '''insert into {} values (?, ?, ?, ?, ?, ?, ?, ?, ?)'''.format(table_name) if deal else '''insert into {} 
    values (?, ?, ?, ?, ?)'''.format(table_name)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
    except sqlite3.Error as e:
        print(e)


def create_stats_table(conn, bots, filename):
    with open(filename) as file:
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
    explorations = [[1/sqrt(2), 1/sqrt(2)]]
    db = {'file': 'data/evaluator_stats.db'}

    bot_names = []
    # bot_names.append(['absolute_result', 'kbs'])
    # bot_names.append(['absolute_result', 'random'])
    # bot_names.append(['absolute_result', 'absolute_result_with_history'])
    # bot_names.append(['absolute_result_with_history', 'score_strength_with_history'])
    # bot_names.append(['absolute_result_with_history', 'kbs'])
    # bot_names.append(['absolute_result_with_history', 'random'])
    # bot_names.append(['score_strength_with_history', 'kbs'])
    # bot_names.append(['score_strength_with_history', 'random'])
    # bot_names.append(['kbs', 'random'])
    bot_names.append(['absolute_result', 'cheat'])
    # bot_names.append(['absolute_result_with_history', 'cheat'])
    # bot_names.append(['cheat', 'kbs'])
    # bot_names.append(['cheat', 'random'])
    histories = []
    # histories.append([False, None])
    # histories.append([False, None])
    # histories.append([False, True])
    # histories.append([True, True])
    # histories.append([True, None])
    # histories.append([True, None])
    # histories.append([True, None])
    # histories.append([True, None])
    # histories.append([None, None])
    histories.append([False, False])
    # histories.append([True, False])
    # histories.append([None, None])
    # histories.append([None, None])

    for e in explorations:
        for i in range(len(bot_names)):
            if any(True for x in histories[i] if x is None):
                iter_max = 2000
            else:
                iter_max = 5000
            evaluate_bots_parallel(bot_names[i], db, games, iter_max, e, histories[i])
