import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from collections import defaultdict, OrderedDict, Counter
from regex_patterns import find_groups
from regex_patterns import find_mentions
from regex_patterns import find_code
from fuzzywuzzy import fuzz
import configparser


class Processor:
    def __init__(self, db_conn, df_questions, df_answers, df_comments, df_edits, filter_user, naive):
        self.conn = db_conn
        self.questions = df_questions
        self.answers = df_answers
        self.comments = df_comments
        self.edits = df_edits
        self.filter_user = filter_user
        self.naive = naive

        self.__config = configparser.ConfigParser()
        self.__config.read("src/config.ini")

        self.stats = []
        self.total_marked_updates = 0
        # This is to keep track of how many comments are connected to an edit that are labelled "update"
        self.comments_per_edit = defaultdict(int)
        self.edits_per_answer = dict()
        self.comments_per_answer = dict()

    def process(self):

        self.process_answers()

        self.write_files()

    def process_answers(self):
        for answer in self.answers.itertuples():
            self.process_comments(answer)

    def process_comments(self, answer):

        answer_id = getattr(answer, "PostId")
        answer_author = str(getattr(answer, "UserName")).strip()

        comments = self.comments.loc[self.comments["PostId"] == answer_id]
        sorted_comments = comments.sort_values(by=['CreationDate'])
        self.comments_per_answer[str(answer_id)] = comments.shape[0]

        # We want to preserve the ordering on the comments we see
        comment_authors = OrderedDict()

        for comment_index, comment in enumerate(sorted_comments.itertuples(), 1):
            # Keep track of comment authors and their position
            comment_author = str(getattr(comment, "UserName")).strip()
            if comment_author in comment_authors:
                comment_authors[comment_author] += 1
            else:
                comment_authors[comment_author] = 1

            # Process all the edits given a comment
            comment_results = self.process_edits(answer, comment)

            # Keep track of user mentions and OP replies in comments
            comment_replies = []

            # Check all previous commenters to see if they have a match with the found mention
            comment_text = getattr(comment, "Text")
            user_mentions = find_mentions(comment_text)
            if len(user_mentions) > 0:
                for mentioned_user in user_mentions:
                    for prev_author, count in comment_authors.items():
                        # Remove the '@' in front of the name
                        if fuzz.ratio(mentioned_user[1:], prev_author) > 95:
                            comment_replies.append((mentioned_user[1:], comment_author))
            # Handle the case where the OP makes a comment but not in reference to someone else
            elif comment_author == answer_author:
                comment_replies.append(("N/A", comment_author))

            # Get the regex groups that the comment matches
            # Combine the comment code and keywords found
            comment_groups = list(set(find_groups(comment_text)) | set(find_code(comment_text)))

            question = self.questions.loc[self.questions["PostId"] == getattr(answer, "ParentId")]
            self.stats.append([question[["PostId"]].to_string(index=False, header=False),
                              answer_id,
                              getattr(comment, "EventId"),
                              question[["UserName"]].to_string(index=False, header=False),
                              answer_author,
                              comment_author,
                              getattr(answer, "Score"),
                              question[["Tags"]].to_string(index=False, header=False),
                              comment_index,
                              getattr(comment, "CreationDate"),
                              getattr(comment, "Score"),
                              getattr(comment, "Text"),
                              comment_groups if len(comment_groups) > 0 else "",
                              comment_results["has_edits"],
                              comment_results["relevant_code_matches"] if len(comment_results["relevant_code_matches"]) > 0 else "",
                              comment_results["edit_id"],
                              comment_results["edit_author"],
                              comment_results["edit_date"],
                              comment_results["edits_by_author"],
                              comment_results["edits_by_others"],
                              comment_replies if len(comment_replies) > 0 else ""])

    def process_edits(self, answer, comment):

        answer_id = getattr(answer, "PostId")
        answer_author = str(getattr(answer, "UserName")).strip()

        edits = self.edits.loc[self.edits["PostId"] == answer_id]
        sorted_edits = edits.sort_values(by=['CreationDate'])
        self.edits_per_answer[str(answer_id)] = edits.shape[0]

        comment_date = getattr(comment, "CreationDate")
        comment_text = getattr(comment, "Text")
        comment_author = str(getattr(comment, "UserName")).strip()
        # Get the regex groups that the comment matches
        # We do not care about cardinality here. We just want to know what were the code terms suggested
        comment_groups = list(set(find_groups(comment_text)) | set(find_code(comment_text)))

        # Boolean if comment has any edits afterward
        has_edits = False
        # Boolean if comment should be marked as update
        mark_as_update = False

        # Keep track of how many edits are by the OP and how many by others
        edits_by_author = 0
        edits_by_others = 0

        # Keep track of which edits have a code match (Edit Index, Code)
        relevant_code_matches = []
        edit_id = None
        edit_author = ""
        edit_date = ""
        # The answer is the initial body of the answer
        prev_edit = answer
        if len(comment_groups) != 0:
            # We start the index from two so it is easier to compare with the stack overflow revision page
            for _, edit in enumerate(sorted_edits.itertuples(), 2):
                edit_date = getattr(edit, "CreationDate")
                edit_author = str(getattr(edit, "UserName")).strip()
                # Only look at the edit if it occurred strictly after the comment
                if comment_date < edit_date:
                    has_edits = True
                    # Keep a counter of which authors make an edit
                    if edit_author == answer_author:
                        edits_by_author += 1
                    else:
                        edits_by_others += 1

                    if self.naive:
                        mark_as_update = True
                        edit_id = getattr(edit, "EventId")
                        edit_date = getattr(edit, "CreationDate")
                        self.comments_per_edit[edit_id] += 1
                        # This code requires running sqlite3 V3.25 or higher
                        query = "SELECT Event, EventId, ROW_NUMBER() OVER (ORDER BY CreationDate) RowNum, CreationDate FROM EditHistory WHERE Event <> 'Comment' AND PostId = {};".format(
                            answer_id)
                        edit_ids = pd.read_sql_query(query, self.conn,
                                                     parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
                        edit_index = int(
                            edit_ids[edit_ids["EventId"] == edit_id][["RowNum"]].to_string(index=False, header=False))
                        relevant_code_matches.append((edit_index, comment_groups))
                        # Otherwise use this
                        # relevant_code_matches.append((edit_id, comment_groups))
                        break
                    else:
                        # If we are filtering users and the comment author and edit author are the same then skip this edit
                        if self.filter_user and comment_author == edit_author:
                            prev_edit = edit
                            continue

                        prev_edit_groups = find_groups(getattr(prev_edit, "Text"))
                        edit_groups = find_groups(getattr(edit, "Text"))
                        # Determine if the edit has the same groups as the comment
                        # We need to take cardinality of matched groups into account because we are looking for more than
                        # existence. i.e., if an edit adds a missing method call we should keep track of that. Not just
                        # whether or not that method was called at all
                        # Taken from https://www.geeksforgeeks.org/python-difference-of-two-lists-including-duplicates/
                        # by user manjeet_04 on Dec 6, 2019 at 13:51 MDT
                        res1 = list((Counter(edit_groups) - Counter(prev_edit_groups)).elements())
                        res2 = list((Counter(prev_edit_groups) - Counter(edit_groups)).elements())
                        matches = self.find_matches(comment_groups, (res1 + res2))
                        if len(matches) > 0:
                            mark_as_update = True
                            edit_id = getattr(edit, "EventId")
                            edit_date = getattr(edit, "CreationDate")
                            self.comments_per_edit[edit_id] += 1
                            # This code requires running sqlite3 V3.25 or higher
                            query = "SELECT Event, EventId, ROW_NUMBER() OVER (ORDER BY CreationDate) RowNum, CreationDate FROM EditHistory WHERE Event <> 'Comment' AND PostId = {};".format(answer_id)
                            edit_ids = pd.read_sql_query(query, self.conn, parse_dates={"CreationDate": "%Y-%m-%d %H:%M:%S"})
                            edit_index = int(edit_ids[edit_ids["EventId"] == edit_id][["RowNum"]].to_string(index=False, header=False))
                            relevant_code_matches.append((edit_index, matches))
                            # Otherwise use this
                            # relevant_code_matches.append((edit_id, matches))
                            break
                prev_edit = edit

            if mark_as_update:
                self.total_marked_updates += 1

        return {
            "has_edits": has_edits,
            "relevant_code_matches": relevant_code_matches,
            "edit_id": edit_id,
            "edit_author": edit_author,
            "edit_date": edit_date,
            "edits_by_author": edits_by_author,
            "edits_by_others": edits_by_others
        }

    # Can not simply take the intersection because sometimes the code is not exact
    # eg. off by a space
    def find_matches(self, list1, list2):
        matches = list()
        for match1 in list1:
            for match2 in list2:
                if fuzz.ratio(match1, match2) >= int(self.__config["PARSER"]["Threshold"]):
                    matches.append(match1)
                    break
        return matches

    def write_files(self):
        # Write stats to csv
        with open("results.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["QuestionId",
                             "AnswerId",
                             "CommentId",
                             "QuestionAuthor",
                             "AnswerAuthor",
                             "CommentAuthor",
                             "AnswerScore",
                             "Tags",
                             "CommentIndex",
                             "CommentDate",
                             "CommentScore",
                             "Comment",
                             "CommentGroups",
                             "HasEditsAfter",
                             "EditGroups(EditIndex,MatchedGroups)",
                             "EditId",
                             "EditAuthor",
                             "EditDate",
                             "EditsByAuthor",
                             "EditsByOthers",
                             "CommentMentions/Replies(MentionedUser,CommentAuthor)"])
            writer.writerows(self.stats)
        f.close()

        comment_edit_dist = defaultdict(int)
        for answer in self.answers.itertuples():
            answer_id = getattr(answer, "PostId")
            edits = self.edits.loc[self.edits["PostId"] == answer_id]
            comments = self.comments.loc[self.comments["PostId"] == answer_id]
            comment_edit_dist[(edits.shape[0], comments.shape[0])] += 1
        x = []
        y = []
        z = []
        for data in comment_edit_dist.items():
            x.append(data[0][0])
            y.append(data[0][1])
            z.append(data[1])

        fig, ax = plt.subplots()
        # fig.set_figheight(10)
        # fig.set_figwidth(15)
        # ax.set_title("Bubble plot of edits and comments")
        ax.set_ylabel("Number of Comments")
        ax.set_xlabel("Number of Edits")
        ax.scatter(x, y, s=[i * 250 for i in z], alpha=0.5)
        # ax.set_xticks(np.arange(0, 22, 2))
        # ax.set_yticks(np.arange(0, 40, 5))
        # Taken from: https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
        # On August 21, 2019 at 13:40 MST
        for size in [1, 2, 5]:
            ax.scatter([], [], alpha=0.5, c="cornflowerblue", s=size * 250, label=str(size))
        ax.legend(labelspacing=2.5, loc="best", markerfirst=False, frameon=False, title="Number of Answers")
        # plt.show()
        plt.savefig("BubblePlot.png")

        # Write statistics to text file
        file = open("stats.txt", "w")
        file.write("Total answers analyzed             : " + str(self.answers.shape[0]) + "\n")
        file.write("Total edits analyzed               : " + str(self.edits.shape[0]) + "\n")
        file.write("Total comments analyzed            : " + str(self.comments.shape[0]) + "\n")
        file.write("Median edits per answer            : " + str(np.median(list(self.edits_per_answer.values()))) + "\n")
        file.write("Median comments per answer         : " + str(np.median(list(self.comments_per_answer.values()))) + "\n")
        file.write("Total comments marked as Update    : " + str(self.total_marked_updates) + "\n")
        total = 0
        for value in self.comments_per_edit.values():
            total += value
        file.write("Average number of comments per edit: "
                   + str(total/len(self.comments_per_edit.keys()) if len(self.comments_per_edit.keys()) > 0 else "0"))
        file.close()
