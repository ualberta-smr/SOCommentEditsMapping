import pandas as pd
import json


def package(db_conn, results_file):
    results = pd.read_csv(results_file, low_memory=False)

    pairs = []
    pair = {
        "Question Id": -1,
        "Answer Id": -1,
        "Tags": "",
        "Comment Id": -1,
        "Edit Id": -1,
        "Comment": "",
        "Before": "",
        "After": "",
        "Confirmed": "",
        "Useful": "",
        "Tangled": "",
        "Category": ""
    }

    for _, row in results.iterrows():
        # Only make entries for matched pairs
        if not pd.isna(row["EditId"]):
            pair["Question Id"] = int(row["QuestionId"])
            answer_id = int(row["AnswerId"])
            pair["Answer Id"] = answer_id
            pair["Tags"] = row["Tags"]
            pair["Comment Id"] = int(row["CommentId"])
            edit_id = int(row["EditId"])
            pair["Edit Id"] = edit_id
            pair["Comment"] = str(row["Comment"])

            # PostHistoryId is the EventId
            query = "SELECT PostHistoryId, LocalId, Content FROM PostBlockVersion WHERE PostId = {} ORDER BY PostHistoryId;".format(answer_id)
            edits = pd.read_sql_query(query, db_conn)
            for edit_index, edit in edits.iterrows():
                if edit["PostHistoryId"] == edit_id:
                    prev_edit_id = edits.iloc[edit_index - 1]["PostHistoryId"]
                    edit_snippets = edits.loc[edits["PostHistoryId"] == edit_id]
                    prev_edit_snippets = edits.loc[edits["PostHistoryId"] == prev_edit_id]

                    # TODO: Loop through all the snippets in the previous edit and the current edit
                    # Sometimes they do not have the same number of snippets (Use localId for matching)
                    before = []
                    after = []
                    # TODO: May have to loop through all prev_edit_snippets too in case of deletion
                    for snip_index, snippet in edit_snippets.iterrows():
                        edit_snippet = str(getattr(snippet, "Content"))
                        prev_edit_snippet = str(getattr(prev_edit_snippets.loc[prev_edit_snippets["LocalId"] == snippet["LocalId"]], "Content"))
                        if edit_snippet != prev_edit_snippet:
                            local_id = snippet["LocalId"]
                            # This try is in the event that the change is a pure addition and there is no previous
                            try:
                                # Check if we are at the first block
                                if local_id != 1:
                                    before.append(str(getattr(prev_edit_snippets.loc[prev_edit_snippets["LocalId"] == (local_id - 1)], "Content")))
                                before.append(prev_edit_snippet)
                                # This try is for the case that the local_id is the last block
                                try:
                                    before.append(str(getattr(prev_edit_snippets.loc[prev_edit_snippets["LocalId"] == (local_id + 1)], "Content")))
                                except:
                                    pass
                            except:
                                pass

                            after.append(str(getattr(edit_snippets.loc[edit_snippets["LocalId"] == (local_id - 1)], "Content")))
                            after.append(edit_snippet)
                            after.append(str(getattr(edit_snippets.loc[edit_snippets["LocalId"] == (local_id + 1)], "Content")))

                    pair["Before"] = '\n'.join(before)
                    pair["After"] = '\n'.join(after)
            pair["Confirmed"] = int(row["Confirmed"]) if "Confirmed" in row and not pd.isnull(row["Confirmed"]) else ""
            pair["Useful"] = int(row["Useful"]) if "Useful" in row and not pd.isna(row["Useful"]) else ""
            pair["Tangled"] = int(row["Tangled"]) if "Tangled" in row and not pd.isna(row["Tangled"]) else ""
            pair["Category"] = row["Category"] if "Category" in row else ""
            pairs.append(json.dumps(pair.copy()))

    with open("results.json", "w") as output:
        output.write(json.dumps(pairs))

