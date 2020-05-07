import argparse
import sqlite3
import time
import pandas as pd

from generate import generate_result_stats, generate_simple_csvs, generate_stat_csv, get_tags
from processor import Processor
from evaluate import evaluate
from package import package


def setup_sqlite(conn):
    c = conn.cursor()
    create_edit_history = open("sql/EditHistory.sql", "r")
    script = create_edit_history.read()
    create_edit_history.close()
    c.executescript(script)
    conn.commit()

    create_smr_tables = open("sql/EditHistory_Code.sql", "r")
    script = create_smr_tables.read()
    create_smr_tables.close()
    c.executescript(script)
    conn.commit()

    c.close()


def create_subquery():
    tags = get_tags()
    sub_query = "SELECT DISTINCT PostId FROM EditHistory WHERE Tags LIKE '%{}%'".format(tags[0])
    for tag in tags[1:]:
        sub_query += " OR Tags LIKE '%{}%'".format(tag)
    return sub_query


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM EditHistory_Code WHERE Event = 'InitialBody' AND PostId IN ("
                                   "SELECT DISTINCT PostId FROM EditHistory WHERE ParentId IN ("
                                   + create_subquery() + "));",
                                   conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query("SELECT * FROM EditHistory_Code WHERE Event = 'Comment' AND PostId IN ("
                                    "SELECT DISTINCT PostId FROM EditHistory WHERE ParentId IN ("
                                    + create_subquery() + "));",
                                    conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query("SELECT * FROM EditHistory_Code WHERE Event = 'BodyEdit' AND PostId IN ("
                                 "SELECT DISTINCT PostId FROM EditHistory WHERE ParentId IN ("
                                 + create_subquery() + "));",
                                 conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_questions = pd.read_sql_query("SELECT * FROM EditHistory WHERE Event = 'InitialBody' AND PostId IN ("
                                     + create_subquery() + ");",
                                     conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})

    return df_questions, df_answers, df_comments, df_edits


def full(clean, filter_user, naive):
    conn = sqlite3.connect("sotorrent.sqlite3")
    print("Connection made")
    if clean:
        setup_sqlite(conn)
    start = time.time()
    df_questions, df_answers, df_comments, df_edits = get_data(conn)
    end = time.time()
    print("Data loading took {0:2f} seconds".format(end - start))

    pipeline = Processor(conn, df_questions, df_answers, df_comments, df_edits, filter_user, naive)
    start = time.time()
    pipeline.process()
    end = time.time()
    print("Took {0:2f} seconds to process".format(end - start))

    # Generate the statistics
    stats()

    # Package the results into JSON
    package(conn, "results.csv")
    print("Finished packaging pairs into JSON")
    conn.close()


def stats():
    start = time.time()

    generate_result_stats()
    generate_simple_csvs()
    # generate_stat_csv()

    end = time.time()

    print("Took {0:2f} seconds to generate files".format(end - start))


def main():
    parser = argparse.ArgumentParser(description="SOTorrent - Comment Induced Updates")
    parser.add_argument("--type", "-t", help="Type of Analysis: Full, Stats", type=str, default="full")
    parser.add_argument("--clean", "-c", help="Make SQL Tables: True, False", type=str, default="t")
    parser.add_argument("--user", "-u", help="Allow commenters to also be editors: True, False", type=str, default="f")
    parser.add_argument("--naive", "-n", help="Naively pair comments and edits by time: True, False",
                        type=str, default="f")
    parser.add_argument("--eval", "-e",
                        help="Evaluate the program against a ground truth (provide ground_truth.csv): True, False",
                        type=str, default="f")
    parser.add_argument("--pack", "-p", help="Package the results into JSON format: <filename>.csv", type=str)

    arg_type = parser.parse_args().type.lower()

    if parser.parse_args().eval.lower()[:1] == "t":
        evaluate()
    elif parser.parse_args().pack and parser.parse_args().pack.lower()[-3:] == "csv":
        conn = sqlite3.connect("sotorrent.sqlite3")
        package(conn, parser.parse_args().pack.lower())
        conn.close()
    else:
        if arg_type == "full":
            arg_clean = True if parser.parse_args().clean.lower()[:1] == "t" else False
            arg_filter_user = True if parser.parse_args().user.lower()[:1] == "f" else False
            arg_naive = True if parser.parse_args().naive.lower()[:1] == "t" else False

            full(arg_clean, arg_filter_user, arg_naive)
        elif arg_type == "stats":
            stats()


main()
