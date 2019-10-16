import argparse
import sqlite3
import time
import pandas as pd

from generate import generate_result_stats, generate_simple_csvs
from processor import Processor


def setup_sqlite(conn):
    c = conn.cursor()
    create_edit_history = open("sql/EditHistory.sql", "r")
    script = create_edit_history.read()
    create_edit_history.close()
    c.executescript(script)
    conn.commit()

    create_smr_tables = open("sql/EditHistory_SMR.sql", "r")
    script = create_smr_tables.read()
    create_smr_tables.close()
    c.executescript(script)
    conn.commit()

    create_results = open("sql/Results.sql", "r")
    script = create_results.read()
    create_results.close()
    c.executescript(script)
    conn.commit()

    c.close()


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'InitialBody';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'Comment';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query("SELECT * FROM EditHistory_SMR WHERE Event = 'BodyEdit';", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_questions = pd.read_sql_query("SELECT * FROM EditHistory WHERE Event = 'InitialBody' AND PostId IN (SELECT DISTINCT ParentId FROM EditHistory WHERE PostId IN (SELECT PostId from EditHistory_SMR));", conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})

    return df_questions, df_answers, df_comments, df_edits


def full(clean):
    conn = sqlite3.connect("sotorrent.sqlite3")
    print("Connection made")
    if clean:
        setup_sqlite(conn)
    start = time.time()
    df_questions, df_answers, df_comments, df_edits = get_data(conn)
    end = time.time()
    print("Data loading took {0:2f} seconds".format(end - start))

    pipeline = Processor(conn, df_questions, df_answers, df_comments, df_edits)
    start = time.time()
    pipeline.process()
    end = time.time()
    conn.close()
    print("Took {0:2f} seconds to process".format(end - start))

    # Generate the statistics
    stats()


def stats():
    start = time.time()

    generate_result_stats()
    generate_simple_csvs()

    end = time.time()

    print("Took {0:2f} seconds to generate files".format(end - start))


def main():
    parser = argparse.ArgumentParser(description="SOTorrent - Comment Induced Updates")
    parser.add_argument("--type", "-t", help="Type of Analysis: Full, Stats", type=str, default="full")
    parser.add_argument("--clean", "-c", help="Make SQL Tables: True, False", type=str, default="t")

    arg_type = parser.parse_args().type.lower()

    if arg_type == "full":
        arg_clean = True if parser.parse_args().clean.lower()[:1] == "t" else False
        full(arg_clean)
    elif arg_type == "stats":
        stats()


main()
