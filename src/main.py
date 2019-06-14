import argparse
import sqlite3
import time
import pandas as pd

from Processor import Processor


def setup_sqlite(conn):
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE EditHistory AS
        SELECT *
        FROM (
            SELECT
              pv.PostId AS PostId,
              pv.PostTypeId AS PostTypeId,
              ph.Id AS EventId,
              CASE
                WHEN pv.PostHistoryTypeId=2 THEN "InitialBody"
                ELSE "BodyEdit"
              END AS Event,
              u.DisplayName AS UserName,
              pv.CreationDate AS CreationDate,
              p.Tags AS Tags,
              ph.Text AS Text
            FROM PostVersion pv
            JOIN PostHistory ph ON pv.PostHistoryId = ph.Id
            JOIN Users u ON ph.UserId = u.Id
            JOIN Posts p ON pv.PostId = p.Id
            WHERE p.Id IN (SELECT PostId FROM PostBlockVersion WHERE PostBlockTypeId = 2)
            UNION ALL
            SELECT
              PostId,
              PostTypeId,
              c.Id AS EventId,
              "Comment" AS Event,
              u.DisplayName AS UserName,
              c.CreationDate AS CreationDate,
              p.Tags As Tags,
              c.Text AS Text
            FROM Comments c
            JOIN Posts p ON c.PostId = p.Id
            JOIN Users u ON c.UserId = u.Id
        ) AS EditHistory;
        
        CREATE INDEX EditHistoryPostIdIndex ON EditHistory(PostId);
        CREATE INDEX EditHistoryEventIdIndex ON EditHistory(EventId);
    ''')

    conn.commit()
    c.close()


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM EditHistory WHERE PostTypeId = 2 AND Event = 'InitialBody';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query("SELECT * FROM EditHistory WHERE Event = 'Comment';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query("SELECT * FROM EditHistory WHERE Event = 'InitialBody' OR Event = 'BodyEdit';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    
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
    pipeline.post_process()
    pipeline.stats()

    end = time.time()

    print("Took {0:2f} seconds".format(end - start))


def post_process():
    pipeline = Processor(None, None, None)

    start = time.time()

    pipeline.post_process()

    end = time.time()

    print("Took {0:2f} seconds".format(end - start))


def stats():
    pipeline = Processor(None, None, None)

    start = time.time()

    pipeline.stats()

    end = time.time()

    print("Took {0:2f} seconds".format(end - start))


def main():
    parser = argparse.ArgumentParser(description="SOTorrent - Comment Induced Updates")
    parser.add_argument("--type", "-t", help="Type of Analysis: Full, Post_Process, Stats", type=str, default="full")

    arg_type = parser.parse_args().type.lower()

    if arg_type == "full":
        full()
    elif arg_type == "post_process":
        post_process()
    elif arg_type == "stats":
        stats()


main()
