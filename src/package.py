import pandas as pd
import json


def package(db_conn, results_file):
    results = pd.read_csv(results_file)

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

            query = "SELECT EventId, Text FROM EditHistory_Code WHERE Event <> 'Comment' AND PostId = {} ORDER BY CreationDate".format(answer_id)
            edits = pd.read_sql_query(query, db_conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
            for edit_index, edit in edits.iterrows():
                if edit["EventId"] == edit_id:
                    prev_edit = edits.iloc[edit_index - 1]
                    pair["Before"] = str(prev_edit["Text"])
                    pair["After"] = str(edit["Text"])
                    break
            pair["Confirmed"] = int(row["Confirmed"]) if "Confirmed" in row and not pd.isnull(row["Confirmed"]) else ""
            pair["Useful"] = int(row["Useful"]) if "Useful" in row and not pd.isna(row["Useful"]) else ""
            pair["Tangled"] = int(row["Tangled"]) if "Tangled" in row and not pd.isna(row["Tangled"]) else ""
            pair["Category"] = row["Category"] if "Category" in row else ""
            pairs.append(json.dumps(pair.copy()))

    with open("results.json", "w") as output:
        output.write(json.dumps(pairs))

