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
    sub_query = "SELECT DISTINCT PostId FROM EditHistory_Code WHERE Tags LIKE '%{}%'".format(tags[0])
    for tag in tags[1:]:
        sub_query += " OR Tags LIKE '%{}%'".format(tag)
    return sub_query


def get_data(conn):
    df_answers = pd.read_sql_query(
        "SELECT * FROM EditHistory_Code WHERE Event = 'InitialBody' AND PostId IN (211161,240165,7416218,8949391,10209691,12609830,15182578,16184827,25776305,26147953,28650939,29052353,31170733,40142454,42895780,49516025,50130390,52347606,53559269,53574609,276739,389793,2204253,10276157,10971756,12110466,22459325,28434849,34459380,36957365,39807014,42207218,43163333,43210935,50817638,52609908,53879119,54574479,55781177,55801335,40189,151940,4009133,4233898,9749510,12903280,18289746,24548749,25860071,29380845,31786638,32050571,33110852,37294534,39806193,40029073,43212125,43673662,45294926,46913880,62680,273206,9890599,15593865,24823645,29684940,29998062,30254825,30933006,34767888,36487361,40551277,40891043,44765572,48484562,51211968,52736206,53243923,54301780,54547101,281433,327384,4356295,14854568,17549972,20177965,20865855,21700067,30461539,32772686,32823117,34866541,37760452,45055491,47482066,48703608,49878150,54444184,55026068,55224131);",
        conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_comments = pd.read_sql_query(
        "SELECT * FROM EditHistory_Code WHERE Event = 'Comment' AND PostId IN (211161,240165,7416218,8949391,10209691,12609830,15182578,16184827,25776305,26147953,28650939,29052353,31170733,40142454,42895780,49516025,50130390,52347606,53559269,53574609,276739,389793,2204253,10276157,10971756,12110466,22459325,28434849,34459380,36957365,39807014,42207218,43163333,43210935,50817638,52609908,53879119,54574479,55781177,55801335,40189,151940,4009133,4233898,9749510,12903280,18289746,24548749,25860071,29380845,31786638,32050571,33110852,37294534,39806193,40029073,43212125,43673662,45294926,46913880,62680,273206,9890599,15593865,24823645,29684940,29998062,30254825,30933006,34767888,36487361,40551277,40891043,44765572,48484562,51211968,52736206,53243923,54301780,54547101,281433,327384,4356295,14854568,17549972,20177965,20865855,21700067,30461539,32772686,32823117,34866541,37760452,45055491,47482066,48703608,49878150,54444184,55026068,55224131);",
        conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_edits = pd.read_sql_query(
        "SELECT * FROM EditHistory_Code WHERE Event = 'BodyEdit' AND PostId IN (211161,240165,7416218,8949391,10209691,12609830,15182578,16184827,25776305,26147953,28650939,29052353,31170733,40142454,42895780,49516025,50130390,52347606,53559269,53574609,276739,389793,2204253,10276157,10971756,12110466,22459325,28434849,34459380,36957365,39807014,42207218,43163333,43210935,50817638,52609908,53879119,54574479,55781177,55801335,40189,151940,4009133,4233898,9749510,12903280,18289746,24548749,25860071,29380845,31786638,32050571,33110852,37294534,39806193,40029073,43212125,43673662,45294926,46913880,62680,273206,9890599,15593865,24823645,29684940,29998062,30254825,30933006,34767888,36487361,40551277,40891043,44765572,48484562,51211968,52736206,53243923,54301780,54547101,281433,327384,4356295,14854568,17549972,20177965,20865855,21700067,30461539,32772686,32823117,34866541,37760452,45055491,47482066,48703608,49878150,54444184,55026068,55224131);",
        conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
    df_questions = pd.read_sql_query(
        "SELECT * FROM EditHistory_Code WHERE Event = 'InitialBody' AND PostId IN (SELECT DISTINCT ParentId FROM EditHistory_Code WHERE PostId IN (211161,240165,7416218,8949391,10209691,12609830,15182578,16184827,25776305,26147953,28650939,29052353,31170733,40142454,42895780,49516025,50130390,52347606,53559269,53574609,276739,389793,2204253,10276157,10971756,12110466,22459325,28434849,34459380,36957365,39807014,42207218,43163333,43210935,50817638,52609908,53879119,54574479,55781177,55801335,40189,151940,4009133,4233898,9749510,12903280,18289746,24548749,25860071,29380845,31786638,32050571,33110852,37294534,39806193,40029073,43212125,43673662,45294926,46913880,62680,273206,9890599,15593865,24823645,29684940,29998062,30254825,30933006,34767888,36487361,40551277,40891043,44765572,48484562,51211968,52736206,53243923,54301780,54547101,281433,327384,4356295,14854568,17549972,20177965,20865855,21700067,30461539,32772686,32823117,34866541,37760452,45055491,47482066,48703608,49878150,54444184,55026068,55224131));",
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
    parser.add_argument("--stage", "-s", help="Stage of Analysis: FULL, STATS, NAIVE, EVAL, PACK", type=str, nargs="+")
    parser.add_argument("--clean", "-c", help="(Re)Make SQL Tables: True, False", type=str, default="T")
    parser.add_argument("--user", "-u", help="Allow commenters to also be editors: True, False", type=str, default="F")

    arg_stage = parser.parse_args().stage[0].upper().strip() if parser.parse_args().stage else None
    if arg_stage is None:
        print("Please specify a stage")
    elif arg_stage == "FULL":
        arg_clean = True if parser.parse_args().clean.upper().strip()[:1] == "T" else False
        arg_filter_user = True if parser.parse_args().user.upper().strip()[:1] == "F" else False
        full(arg_clean, arg_filter_user, False)
    elif arg_stage == "STATS":
        stats()
    elif arg_stage == "NAIVE":
        arg_clean = True if parser.parse_args().clean.upper().strip()[:1] == "T" else False
        arg_filter_user = True if parser.parse_args().user.upper().strip()[:1] == "F" else False
        full(arg_clean, arg_filter_user, True)
    elif arg_stage == "EVAL":
        evaluate()
    elif arg_stage == "PACK":
        try:
            csv = parser.parse_args().stage[1]
            conn = sqlite3.connect("sotorrent.sqlite3")
            package(conn, csv)
            conn.close()
        except IndexError:
            print("Please provide a CSV to pack into JSON")


main()
