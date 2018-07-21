DROP TABLE IF EXISTS {0}_vs_kbs_bot_stats;

CREATE TABLE {0}_vs_kbs_bot_stats
             ( 
                                                 time REAL, 
                          exploration            REAL, 
                          average_{0}_score      REAL, 
                          average_kbs_score      REAL, 
                          {0}_win_percentage     REAL, 
                          kbs_rubicon_percentage REAL 
             );

INSERT INTO {0}_vs_kbs_bot_stats
SELECT average.time, 
       average.exploration, 
       average_{0}_score, 
       average_kbs_score, 
       {0}_wins           * 100.0 / total_games AS {0}_win_percentage, 
       kbs_rubicon_scores * 100.0 / total_games AS kbs_rubicon_percentage 
FROM   ( 
                SELECT   time, 
                         exploration, 
                         avg({0}) AS average_{0}_score, 
                         avg(kbs) AS average_kbs_score 
                FROM     {0}_vs_kbs_bot 
                GROUP BY time, 
                         exploration) AS average 
JOIN 
       ( 
                SELECT   time, 
                         exploration, 
                         count({0}) AS {0}_wins 
                FROM     {0}_vs_kbs_bot 
                WHERE    {0} > kbs 
                GROUP BY time, 
                         exploration) AS {0}_wins 
ON     average.time = {0}_wins.time 
AND    average.exploration = {0}_wins.exploration 
JOIN 
       ( 
                SELECT   time, 
                         exploration, 
                         count(kbs) AS kbs_rubicon_scores 
                FROM     {0}_vs_kbs_bot 
                WHERE    kbs >= 100 
                GROUP BY time, 
                         exploration) AS kbs_rubicon 
ON     average.time = kbs_rubicon.time 
AND    average.exploration = kbs_rubicon.exploration 
JOIN 
       ( 
                SELECT   time, 
                         exploration, 
                         count(*) AS total_games 
                FROM     {0}_vs_kbs_bot 
                GROUP BY time, 
                         exploration) AS games 
ON     average.time = games.time 
AND    average.exploration = games.exploration;
