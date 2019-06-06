import argparse
import sqlite3
import time
import pandas as pd

from Processor import Processor


def setup_sqlite(conn):
    c = conn.cursor()
    c.executescript('''
        DROP TABLE IF EXISTS MSR_QUESTIONS;
        DROP TABLE IF EXISTS MSR_ANSWERS;
        DROP TABLE IF EXISTS MSR_COMMENTS;
        DROP TABLE IF EXISTS MSR_EDITS;
        
        -- Retrieve all the Questions from the Posts table
        CREATE TABLE MSR_QUESTIONS AS
            SELECT p.Id
            FROM Posts p
            LEFT JOIN PostType pt ON p.PostTypeId = pt.Id AND pt.Type = "Question"
            WHERE p.Score > 5
            LIMIT 100;
        
        -- Join Questions with their answers
        CREATE TABLE MSR_ANSWERS AS 
            SELECT a.Id AS ANSWER_ID, 
                q.Id AS QUESTION_ID
            FROM Posts a 
            JOIN MSR_QUESTIONS q ON q.Id = a.ParentId;
        
        -- Get all comments on an answer
        CREATE TABLE MSR_COMMENTS AS
            SELECT c.Id AS ID,
                c.PostId AS POST_ID,
                c.Text AS TEXT,
                c.CreationDate AS CREATION_DATE
            FROM Comments c 
            LEFT JOIN MSR_ANSWERS a ON c.PostId = a.ANSWER_ID;
        
        -- Get all edits on an answer  
        CREATE TABLE MSR_EDITS AS 
            SELECT b.Id AS ID,
                b.PostId AS POST_ID,
                b.PostHistoryId AS POST_HISTORY_ID,
                h.CreationDate AS UPDATE_DATE,
                b.Content AS CONTENT
            FROM PostBlockVersion b
            JOIN PostHistory h ON b.PostHistoryId = h.Id
            LEFT JOIN PostBlockType pbt ON pbt.Id = b.PostBlockTypeId AND pbt.Type = "CodeBlock"
            WHERE b.PostId IN (
                SELECT ANSWER_ID
                FROM MSR_ANSWERS
            )
            AND (b.PredEqual IS NULL OR b.PredEqual = 0)
            ORDER BY POST_HISTORY_ID ASC 
    ''')

    conn.commit()
    c.close()


def get_data(conn):

    df_answers = pd.read_sql_query("SELECT * FROM MSR_ANSWERS;", conn)

    print("Retrieved answers", df_answers.size)

    df_comments = pd.read_sql_query("SELECT * FROM MSR_COMMENTS;", conn)

    print("Retrieved comments", df_comments.size)

    df_edits = pd.read_sql_query("SELECT * FROM MSR_EDITS;", conn)

    print("Retrieved edits", df_edits.size)

    return df_answers, df_comments, df_edits


def full():
    # conn = sqlite3.connect("sotorrent.sqlite3")
    conn = sqlite3.connect("src/test.sqlite3")
    print("connection made")
    # setup_sqlite(conn)
    df_answers, df_comments, df_edits = get_data(conn)

    conn.close()

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
