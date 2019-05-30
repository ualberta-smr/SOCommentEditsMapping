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
            AND (b.PredEqual IS NULL OR PredEqual = 0)
            ORDER BY POST_HISTORY_ID ASC 
    ''')

    conn.commit()
    c.close()


def get_data(conn):
    c = conn.cursor()

    answers = c.execute("SELECT * FROM MSR_ANSWERS")
    comments = c.execute("SELECT * FROM MSR_COMMENTS")
    edits = c.execute("SELECT * FROM MSR_EDITS")

    df_answers = pd.DataFrame(answers, columns=["AnswerId", "QuestionId"])
    df_comments = pd.DataFrame(comments, columns=["Id", "PostId", "Text", "CreationDate"])
    df_edits = pd.DataFrame(edits, columns=["Id", "PostId", "RootHistoryId", "RootPostBlockVersionId", "PredEqual", "PredSimilarity", "Length", "RootLocalId", "UpdatedAt", "Content"])

    c.close()

    return df_answers, df_comments, df_edits


def full():
    conn = sqlite3.connect("sotorrent.sqlite3")
    setup_sqlite(conn)
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
