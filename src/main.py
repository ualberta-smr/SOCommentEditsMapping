import argparse
import sqlite3
import time
import pandas as pd

from processor import Processor


def setup_sqlite(conn):
    c = conn.cursor()
    create_edit_history = open("EditHistory.sql", "r")
    script = create_edit_history.read()
    create_edit_history.close()
    c.executescript(script)
    conn.commit()

    create_smr_tables = open("EditHistory_SMR.sql", "r")
    script = create_smr_tables.read()
    create_smr_tables.close()
    c.executescript(script)
    conn.commit()
    c.close()


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'InitialBody';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'Comment';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'BodyEdit';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})

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
