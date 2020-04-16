import pandas as pd
import re
import numpy as np


def evaluate():
    ground_truth = pd.read_csv('data/ground_truth.csv', index_col=False, parse_dates=["Comment Date"])
    results = pd.read_csv('results.csv')

    true_positives = 0
    marked_positives = 0
    caught_positives = 0
    all_positives = 0
    useful = 0
    seen = []
    for _, ground_truth_row in ground_truth.iterrows():

        if not ground_truth_row["AnswerId"] in seen:
            seen.append(ground_truth_row["AnswerId"])
            # Calculate precision
            # Loop through the relevant results row
            relevant_results = results.loc[results["AnswerId"] == ground_truth_row["AnswerId"]]
            for _, result_row in relevant_results.iterrows():
                # If the program caught something
                if not pd.isnull(result_row["EditGroups(EditIndex,MatchedGroups)"]):
                    caught_edit = re.search(re.compile("(?<=\[\()[0-9]{1,2}"),
                                            result_row["EditGroups(EditIndex,MatchedGroups)"]).group(0)
                    relevant_ground_truth_row = ground_truth.loc[(ground_truth["AnswerId"] == result_row["AnswerId"]) & (
                                ground_truth["CommentId"] == result_row["CommentId"])]
                    # If the ground truth has an edit matched with the current comment
                    if not pd.isnull(relevant_ground_truth_row["EditIds"]):
                        if int(caught_edit) == int(relevant_ground_truth_row["EditIds"]):
                            true_positives += 1
                            # Keep track of if the match is useful
                            if not pd.isnull(ground_truth_row["Useful"]) and re.search(re.compile("Yes|yes"),
                                                                                       relevant_ground_truth_row["Useful"]):
                                useful += 1
                    marked_positives += 1

        # Calculate recall
        # If the comment pair was manually evaluated to cause an edit
        if not pd.isnull(ground_truth_row["EditIds"]):
            # If the program also matched to an edit
            relevant_result = results.loc[
                (results["AnswerId"] == ground_truth_row["AnswerId"]) & (
                            results["CommentId"] == ground_truth_row["CommentId"])]
            if not pd.isnull(relevant_result["EditGroups(EditIndex,MatchedGroups)"]):
                caught_edit = re.search(re.compile("(?<=\[\()[0-9]{1,2}"),
                                        relevant_result["EditGroups(EditIndex,MatchedGroups)"].item()).group(0)
                # And what was caught is the same as what was matched
                if int(caught_edit) == int(ground_truth_row["EditIds"]):
                    caught_positives += 1
            # Keep track of all comments that were manually matched with an edit
            all_positives += 1

    assert true_positives == caught_positives

    precision = true_positives / marked_positives
    recall = caught_positives / all_positives

    useful = useful / true_positives

    print("Precision : %d%%\nRecall    : %d%%\nUseful    : %d%%"
          % (round(precision * 100), round(recall * 100), round(useful * 100)))

    print("Answer IDs not found:",
          np.setdiff1d(np.asarray(ground_truth["AnswerId"].unique().tolist()), np.asarray(seen)))
