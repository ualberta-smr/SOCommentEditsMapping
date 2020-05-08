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
            query = "SELECT PostHistoryId, RootLocalId, GROUP_CONCAT(Content, '\n') AS Text FROM PostBlockVersion WHERE PostBlockTypeId = 2 AND PostId = {} GROUP BY PostHistoryId, RootLocalId ORDER BY PostHistoryId;".format(answer_id)
            edits = pd.read_sql_query(query, db_conn)
            before = []
            after = []
            for edit_index, edit in edits.iterrows():
                if edit["PostHistoryId"] == edit_id:
                    prev_edit_id = edits.iloc[edit_index - 1]["PostHistoryId"]
                    edit_snippets = edits.loc[edits["PostHistoryId"] == edit_id]
                    prev_edit_snippets = edits.loc[edits["PostHistoryId"] == prev_edit_id]
                    for _, edit_snippet in edit_snippets.iterrows():
                        local_id = edit_snippet["RootLocalId"]
                        try:
                            # There may be no prev_snippet if it is a straight addition
                            prev_snippet = prev_edit_snippets.loc[prev_edit_snippets["RootLocalId"] == local_id].iloc[0]
                            if prev_snippet["Text"] != edit_snippet["Text"]:
                                before.append(prev_snippet["Text"])
                                after.append(edit_snippet["Text"])
                        except:
                            after.append(edit_snippet["Text"])

                    for _, prev_snippet in prev_edit_snippets.iterrows():
                        local_id = prev_snippet["RootLocalId"]
                        try:
                            # There may be no edit_snippet if it is a straight deletion
                            edit_snippet = edit_snippets.loc[edit_snippets["RootLocalId"] == local_id].iloc[0]
                            if prev_snippet["Text"] != edit_snippet["Text"]:
                                before.append(prev_snippet["Text"])
                                after.append(edit_snippet["Text"])
                        except:
                            before.append(prev_snippet["Text"])
                    # Remove duplicates while preserving the order
                    seen = set()
                    pair["Before"] = [snip for snip in before if not (snip in seen or seen.add(snip))]
                    pair["After"] = [snip for snip in after if not (snip in seen or seen.add(snip))]
            pair["Confirmed"] = int(row["Confirmed"]) if "Confirmed" in row and not pd.isnull(row["Confirmed"]) else ""
            pair["Useful"] = int(row["Useful"]) if "Useful" in row and not pd.isna(row["Useful"]) else ""
            pair["Tangled"] = int(row["Tangled"]) if "Tangled" in row and not pd.isna(row["Tangled"]) else ""
            pair["Category"] = row["Category"] if "Category" in row else ""
            pairs.append(json.dumps(pair.copy()))
            
    with open("results.json", "w") as output:
        output.write(json.dumps(pairs))

