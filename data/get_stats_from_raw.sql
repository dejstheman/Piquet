drop table if exists absolute_result_vs_kbs_bot_stats;
create table absolute_result_vs_kbs_bot_stats
(
time real,
exploration real,
average_absolute_result_score real,
average_kbs_score real,
absolute_result_win_percentage real,
kbs_rubicon_percentage real
);
insert into absolute_result_vs_kbs_bot_stats
select average.time,
 average.exploration,
 average_absolute_result_score,
 average_kbs_score,
 absolute_result_wins * 100.0 / total_games as absolute_result_win_percentage,
 kbs_rubicon_scores * 100.0 / total_games as kbs_rubicon_percentage
 from
(select time, exploration, avg(absolute_result) as average_absolute_result_score,
avg(kbs) as average_kbs_score
from absolute_result_vs_kbs_bot
group by time, exploration) as average
JOIN (SELECT time,
                    exploration,
                    Count(absolute_result) AS absolute_result_wins
             FROM   absolute_result_vs_kbs_bot
             WHERE  absolute_result > kbs
             GROUP  BY time,
                       exploration) AS absolute_result_wins
         ON average.time = absolute_result_wins.time
            AND average.exploration = absolute_result_wins.exploration
       JOIN (SELECT time,
                    exploration,
                    Count(kbs) AS kbs_rubicon_scores
             FROM   absolute_result_vs_kbs_bot
             WHERE  kbs >= 100
             GROUP  BY time,
                       exploration) AS kbs_rubicon
         ON average.time = kbs_rubicon.time
            AND average.exploration = kbs_rubicon.exploration
       JOIN (SELECT time,
                    exploration,
                    Count(*) AS total_games
             FROM   absolute_result_vs_kbs_bot
             GROUP  BY time,
                       exploration) AS games
         ON average.time = games.time
            AND average.exploration = games.exploration;
