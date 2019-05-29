import argparse
import sqlite3
import time
import pandas as pd

from Processor import Processor


def setup_sqlite():
    conn = sqlite3.connect("sotorrent.sqlite3")
    c = conn.cursor()

    answers = c.execute("SELECT * FROM MSR_Answers")
    comments = c.execute("SELECT * FROM MSR_Comments")
    edits = c.execute("SELECT * FROM MSR_Edits")

    df_answers = pd.DataFrame(answers, columns=["AnswerId", "QuestionId"])
    df_comments = pd.DataFrame(comments, columns=["Id", "PostId", "Text", "CreationDate"])
    df_edits = pd.DataFrame(edits, columns=["Id", "PostId", "RootHistoryId", "RootPostBlockVersionId", "PredEqual", "PredSimilarity", "Length", "RootLocalId", "UpdatedAt", "Content"])

    return df_answers, df_comments, df_edits


def full():
    df_answers, df_comments, df_edits = setup_sqlite()
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
