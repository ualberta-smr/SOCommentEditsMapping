import pandas as pd
import re


def evaluate():
    ground_truth = pd.read_csv('ground_truth.csv', index_col=False, parse_dates=["Comment Date"])

    true_positives = 0
    marked_positives = 0
    caught_positives = 0
    all_positives = 0
    useful = 0
    for index, row in ground_truth.iterrows():
        # If the program caught something
        if not pd.isnull(row["EditGroups"]):
            edit = re.search(re.compile("(?<=\[\()[0-9]{1,2}"), row["EditGroups"]).group(0)
            # If the ground truth matches an edit with the comment
            if not pd.isnull(row["EditIds"]):
                # If what the program caught and what was marked is the same
                if int(edit) == int(row["EditIds"]):
                    true_positives += 1
                    # Keep track of if the match is useful
                    if re.search(re.compile("Yes|yes"), row["Useful"]):
                        useful += 1
            # Regardless of if the ground truth marks the comment, the program found something so keep track of it
            marked_positives += 1

        # This is if the program did not catch anything but the comment was matched to an edit
        if not pd.isnull(row["EditIds"]):
            # If however the program did catch something
            if not pd.isnull(row["EditGroups"]):
                edit = re.search(re.compile("(?<=\[\()[0-9]{1,2}"), row["EditGroups"]).group(0)
                # And what was caught is the same as what was matched
                if int(edit) == int(row["EditIds"]):
                    caught_positives += 1
            # Keep track of all comments that were manually matched with an edit
            all_positives += 1

    assert true_positives == caught_positives

    precision = true_positives / marked_positives
    recall = caught_positives / all_positives

    useful = useful / true_positives

    print("Precision : %d%%\nRecall    : %d%%\nUseful    : %d%%"
          % (round(precision * 100), round(recall * 100), round(useful * 100)))
