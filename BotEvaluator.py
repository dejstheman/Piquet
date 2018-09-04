import multiprocessing
import random
import sqlite3
from copy import deepcopy
from math import sqrt

from joblib import Parallel, delayed

from DealState import DealState
from DealISMCTS import deal_ismcts, deal_ismcts_decisive
from DealKBS import deal_kbs


def create_partie(players, scores):
    return [DealState(players, scores) if x % 2 == 0 else DealState(players[::-1], scores) for x in range(6)]


def create_sample_games(partie, n):
    return [deepcopy(partie) for _ in range(n)]


def evaluate_bots_parallel(bots, db, games, time_resource, explorations):
    db['table_name'] = '{}_vs_{}_partie_bots'.format(bots[0], bots[1])
    scores = {p: 0 for p in bots}
    partie = create_partie(bots, scores)
    Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(bot_partie)(bots, partie, db, time_resource, explorations)
        for partie in create_sample_games(partie, games))
    conn = create_connection(db['file'])
    with conn:
        create_stats_table(conn, bots, 'data/get_partie_stats_from_table.txt')
        create_stats_table(conn, bots, 'data/get_deal_stats_from_table.txt')


def bot_partie(bots, partie, db, time_resource, explorations):
    conn = create_connection(db['file'])
    current = deepcopy(partie)
    for deal in current:
        e = explorations[bots.index(deal.player_to_play)]
        while deal.get_possible_moves():
            if deal.player_to_play.startswith('kbs'):
                if deal.player_to_play.endswith('greedy'):
                    deal.do_move(deal_kbs(deal, True))
                else:
                    deal.do_move(deal_kbs(deal, False))
            elif deal.player_to_play.startswith('random'):
                deal.do_move(random.choice(deal.get_possible_moves()))
            elif deal.player_to_play.endswith('cheat'):
                deal.do_move(deal_ismcts(
                    root_state=deal, time_resource=time_resource, exploration=e, result_type=deal.player_to_play,
                    history=False, cheat=True))
            elif deal.player_to_play.endswith('decisive'):
                deal.do_move(deal_ismcts_decisive(
                    root_state=deal, time_resource=time_resource, exploration=e, result_type=deal.player_to_play,
                    history=False))
            elif deal.player_to_play.endswith('history'):
                deal.do_move(deal_ismcts(
                    root_state=deal, time_resource=time_resource, exploration=e, result_type=deal.player_to_play,
                    history=True))
            else:
                deal.do_move(deal_ismcts(
                    root_state=deal, time_resource=time_resource, exploration=e, result_type=deal.player_to_play,
                    history=False))
        scores = deal.deal_scores
        values = (time_resource, explorations[0], scores[bots[0]], explorations[1], scores[bots[1]],
                  deal.repique, deal.pique, deal.cards, deal.capot, deal.players[0])
        with conn:
            table_name = db['table_name'].replace('partie', 'deal')
            create_table(conn, table_name, bots, True)
            update_table(conn, table_name, values, True)
    scores = current[0].scores
    values = (time_resource, explorations[0], scores[bots[0]], explorations[1], scores[bots[1]])
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
    sql = '''create table if not exists {0} (time_resource INTEGER, {1}_exploration REAL, {1} INTEGER, {2}_exploration REAL, 
    {2} INTEGER, repique TEXT, pique TEXT, cards TEXT, capot TEXT, elder TEXT);'''.format(table_name, bots[0], bots[1])\
        if deal else '''create table if not exists {0} (
        time_resource INTEGER, {1}_exploration REAL, {1} INTEGER, {2}_exploration REAL, 
    {2} INTEGER);'''.format(table_name, bots[0], bots[1])
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)


def update_table(conn, table_name, data, deal):
    sql = '''insert into {} values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''.format(table_name) if deal else '''insert into {} 
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
    for i in range(1):
        games = 8
        explorations = []
        explorations.append([1/sqrt(2), 1/sqrt(2)])
        # explorations.append([1/sqrt(2), 0.1])
        # explorations.append([1/sqrt(2), 0.5])
        # explorations.append([1/sqrt(2), 1])
        # explorations.append([1/sqrt(2), 2])
        # explorations.append([1/sqrt(2), 2.5])
        # explorations.append([1/sqrt(2), 5])
        # explorations.append([1/sqrt(2), 7.5])
        # explorations.append([1/sqrt(2), 10])
        # explorations.append([1/sqrt(2), 15])
        # explorations.append([1/sqrt(2), 25])
        # explorations.append([1/sqrt(2), 0.6])
        # explorations.append([1/sqrt(2), 0.65])
        # explorations.append([1/sqrt(2), 0.8])
        # explorations.append([1/sqrt(2), 100])
        # explorations.append([1/sqrt(2), 50])
        # explorations.append([1/sqrt(2), 75])
        db = {'file': 'data/evaluator_stats.db'}
        time_resources = [2]

        bot_names = []
        bot_names.append(['absolute_result', 'score_strength'])
        bot_names.append(['absolute_result', 'random'])
        bot_names.append(['absolute_result', 'kbs'])
        bot_names.append(['absolute_result', 'show_result'])
        bot_names.append(['show_result', 'score_strength'])
        # bot_names.append(['score_strength', 'kbs'])
        # bot_names.append(['score_strength', 'random'])
        # bot_names.append(['show_result', 'kbs'])
        # bot_names.append(['show_result', 'random'])
        bot_names.append(['kbs', 'random'])
        bot_names.append(['score_strength', 'kbs'])
        bot_names.append(['random', 'score_strength'])
        # bot_names.append(['absolute_result', 'random'])
        # bot_names.append(['absolute_result', 'kbs'])
        # bot_names.append(['kbs1', 'kbs2'])
        # bot_names.append(['random1', 'random2'])

        # for e in explorations:
        #     for j in range(len(bot_names)):
        #         for time in time_resources:
        #             evaluate_bots_parallel(bot_names[j], db, games, time, e)

        conn = create_connection(db['file'])
        with conn:
            for bot in bot_names:
                create_stats_table(conn, bot, 'data/get_deal_stats_from_table.txt')
                create_stats_table(conn, bot, 'data/get_partie_stats_from_table.txt')
