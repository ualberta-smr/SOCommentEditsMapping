import argparse
import sqlite3
import time
import pandas as pd

from processor import Processor


def setup_sqlite(conn):
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE EditHistory AS
        SELECT *
        FROM (
            SELECT
              pv.PostId AS PostId,
              p.ParentId AS ParentId,
              pv.PostTypeId AS PostTypeId,
              ph.Id AS EventId,
              CASE
                WHEN pv.PostHistoryTypeId=2 THEN "InitialBody"
                ELSE "BodyEdit"
              END AS Event,
              u.DisplayName AS UserName,
              pv.CreationDate AS CreationDate,
              p.Tags AS Tags,
              p.Score AS Score,
              ph.Text AS Text
            FROM PostVersion pv
            JOIN PostHistory ph ON pv.PostHistoryId = ph.Id
            JOIN Users u ON ph.UserId = u.Id
            JOIN Posts p ON pv.PostId = p.Id
            WHERE p.Id IN (SELECT DISTINCT pbv.PostId FROM PostBlockVersion pbv WHERE PostBlockTypeId = 2)
            UNION ALL
            SELECT
              p.Id AS PostId,
              p.ParentId AS ParentId,
              p.PostTypeId AS PostTypeId,
              c.Id AS EventId,
              "Comment" AS Event,
              u.DisplayName AS UserName,
              c.CreationDate AS CreationDate,
              p.Tags AS Tags,
              c.Score AS Score,
              c.Text AS Text
            FROM Comments c
            JOIN Posts p ON c.PostId = p.Id
            JOIN Users u ON c.UserId = u.Id
            WHERE p.Id IN (SELECT DISTINCT pbv.PostId FROM PostBlockVersion pbv WHERE PostBlockTypeId = 2)
        ) AS EditHistory;
        
        CREATE INDEX EditHistoryPostIdIndex ON EditHistory(PostId);
        CREATE INDEX EditHistoryEventIdIndex ON EditHistory(EventId);
    ''')

    conn.commit()
    c.close()


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM EditHistory_MSR WHERE Event = 'InitialBody';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query("SELECT * FROM EditHistory_MSR WHERE Event = 'Comment';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query("SELECT * FROM EditHistory_MSR WHERE Event = 'BodyEdit';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})

    return df_answers, df_comments, df_edits


def full():
    # conn = sqlite3.connect("sotorrent.sqlite3")
    conn = sqlite3.connect("src/test.sqlite3")
    print("connection made")
    # setup_sqlite(conn)
    start = time.time()
    df_answers, df_comments, df_edits = get_data(conn)
    conn.close()
    end = time.time()
    print("Data loading took {0:2f} seconds".format(end - start))

    pipeline = Processor(df_answers, df_comments, df_edits)

    start = time.time()

    pipeline.process()
    pipeline.generate_csvs()

    end = time.time()

    print("Took {0:2f} seconds".format(end - start))


def stats():
    pipeline = Processor(None, None, None)

    start = time.time()

    pipeline.generate_csvs()

    end = time.time()

    print("Took {0:2f} seconds".format(end - start))


def main():
    parser = argparse.ArgumentParser(description="SOTorrent - Comment Induced Updates")
    parser.add_argument("--type", "-t", help="Type of Analysis: Full, Stats", type=str, default="full")

    arg_type = parser.parse_args().type.lower()

    if arg_type == "full":
        full()
    elif arg_type == "stats":
        stats()


main()
