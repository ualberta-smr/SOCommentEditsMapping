import pandas as pd
import datetime
import matplotlib.pyplot as plt


def get_tags():
    with open("src/tags.cfg") as f:
        tags = f.read().splitlines()
    return tags


# The tags argument is a string containing the tags on a question
def find_tags(tags):
    # These are the tags specified in the tag config
    tags_config = get_tags()
    found_tags = []
    for tag in tags_config:
        # If the Tags on the question match a tag in the config then append it
        if tag in tags:
            found_tags.append(tag)
    return found_tags


# Generate different Result statistics based on Tag
def generate_result_stats():
    data = pd.read_csv('results.csv', index_col=False, parse_dates=["CommentDate", "EditDate"])

    data = data.loc[pd.isnull(data["EditGroups(EditId,MatchedGroups)"]) == False]

    tags = get_tags()
    tag_dict = {}
    for tag in tags:
        tag_dict[tag] = {
            "commenter_editor_same": 0,
            "commenter_editor_different": 0,
            "answer_editor_same": 0,
            "answer_editor_different": 0,
            "question_commenter_same": 0,
            "question_commenter_different": 0,
            "response_times": [],
            "num_bad_answers": 0,
            "num_good_answers": 0,
            "scores": []
        }

    # If an answer is tagged with multiple tags found in the tags config
    # Then it will count for both tags
    for row in data.itertuples():
        tags = find_tags(getattr(row, "Tags"))
        for tag in tags:
            # Check to see how many times the commenter is the same as the editor
            if getattr(row, "CommentAuthor").strip() == getattr(row, "EditAuthor").strip():
                tag_dict[tag]["commenter_editor_same"] += 1
            else:
                tag_dict[tag]["commenter_editor_different"] += 1

            # Count how many times the editor is the same as the answer author
            if getattr(row, "AnswerAuthor").strip() == getattr(row, "EditAuthor").strip():
                tag_dict[tag]["answer_editor_same"] += 1
            else:
                tag_dict[tag]["answer_editor_different"] += 1

            # Count how many times the Questioner is the same as the commenter
            if getattr(row, "QuestionAuthor").strip() == getattr(row, "CommentAuthor").strip():
                tag_dict[tag]["question_commenter_same"] += 1
            else:
                tag_dict[tag]["question_commenter_different"] += 1

            tag_dict[tag]["response_times"].append(getattr(row, "EditDate") - getattr(row, "CommentDate"))

            if getattr(row, "AnswerScore") < 0:
                tag_dict[tag]["num_bad_answers"] += 1
            else:
                tag_dict[tag]["num_good_answers"] += 1

            tag_dict[tag]["scores"].append(getattr(row, "AnswerScore"))

    for tag in tag_dict.keys():
        if not tag_dict[tag]["response_times"]:
            tag_dict[tag]["average_response_time"] = pd.NaT
        else:
            tag_dict[tag]["average_response_time"] = \
                sum(tag_dict[tag]["response_times"], datetime.timedelta(0)) / len(tag_dict[tag]["response_times"])

    file = open("result_stats.txt", "w")
    for tag in tag_dict.keys():
        file.write("Tag                             : " + tag + "\n")
        file.write("Commenter/Editor Same           : " + str(tag_dict[tag]["commenter_editor_same"]) + "\n")
        file.write("Commenter/Editor Different      : " + str(tag_dict[tag]["commenter_editor_different"]) + "\n")
        file.write("Answerer/Editor Same            : " + str(tag_dict[tag]["answer_editor_same"]) + "\n")
        file.write("Answerer/Editor Different       : " + str(tag_dict[tag]["answer_editor_different"]) + "\n")
        file.write("Questioner/Commenter Same       : " + str(tag_dict[tag]["question_commenter_same"]) + "\n")
        file.write("Questioner/Commenter Different  : " + str(tag_dict[tag]["question_commenter_different"]) + "\n")
        file.write("Average Response Time           : " + str(tag_dict[tag]["average_response_time"]) + "\n")
        file.write("Num Good Answers                : " + str(tag_dict[tag]["num_good_answers"]) + "\n")
        file.write("Num Bad Answers                 : " + str(tag_dict[tag]["num_bad_answers"]) + "\n")
        file.write("Average Answer Score            : " + str(sum(tag_dict[tag]["scores"]) / len(tag_dict[tag]["scores"]) if len(tag_dict[tag]["scores"]) else "") + "\n")
        file.write("\n")
    file.close()

    fig, ax = plt.subplots()
    # ax.set_title("Distribution of Answer Scores")
    ax.set_ylabel("Number of Answers")
    ax.set_xlabel("Answer Score")
    ax.hist(data['AnswerScore'].tolist())
    # plt.show()
    plt.savefig("AnswerDistribution.png")


def generate_simple_csvs():
    data = pd.read_csv('results.csv', index_col=False, parse_dates=["CommentDate", "EditDate"])
    data = data.loc[pd.isnull(data["EditGroups(EditId,MatchedGroups)"]) == False]

    tags = get_tags()
    for tag in tags:
        # Taken from https://stackoverflow.com/questions/11350770/select-by-partial-string-from-a-pandas-dataframe
        # User Garrett on Oct 2, 2019 at 14:26 MDT
        tag_data = data[data["Tags"].str.contains(tag)]
        data_to_write = tag_data[["AnswerId",
                                  "CommentId",
                                  "CommentAuthor",
                                  "CommentDate",
                                  "CommentIndex",
                                  "EditGroups(EditId,MatchedGroups)",
                                  "EditId"
                                  ]]
        data_to_write.to_csv(path_or_buf='results_' + tag[1:-1] + '.csv', index=False)
