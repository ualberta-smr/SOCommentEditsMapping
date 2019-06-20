import csv
import matplotlib.pyplot as plt

from collections import defaultdict, OrderedDict
from RegexPatterns import find_groups
from RegexPatterns import find_mentions
from RegexPatterns import find_code


def get_tags():
    with open("src/tags.cfg") as f:
        tags = f.read().splitlines()

    return tags


class Processor:

    def __init__(self, df_answers, df_comments, df_edits):
        self.answers = df_answers
        self.comments = df_comments
        self.edits = df_edits

        self.dataset = []

    def process(self):
        # Keep track of stats to write to csv
        stats = []

        total_answers = self.answers.shape[0]
        total_comments = self.comments.shape[0]
        total_updates = 0
        edit_updates = defaultdict(int)
        answer_edits = dict()
        for answer in self.answers.itertuples():
            # Get the author of the answer
            answer_author = getattr(answer, "UserName")
            answer_id = getattr(answer, "PostId")

            # Retrieve all the comments and edits on this answer and sort them ascending by time
            comments = self.comments.loc[self.comments["PostId"] == answer_id]
            sorted_comments = comments.sort_values(by=['CreationDate'])
            edits = self.edits.loc[self.edits["PostId"] == answer_id]
            sorted_edits = edits.sort_values(by=['CreationDate'])

            answer_edits[str(answer_id)] = sorted_edits.shape[0]

            # We want to preserve the ordering on the comments we see
            comment_authors = OrderedDict()

            for comment_index, comment in enumerate(sorted_comments.itertuples(), 1):
                has_edits = False

                # Keep track of comment authors and their position
                comment_author = getattr(comment, "UserName")
                if comment_author in comment_authors:
                    comment_authors[comment_author] += 1
                else:
                    comment_authors[comment_author] = 1

                # Keep track of user mentions and OP replies in comments
                comment_replies = []

                comment_text = getattr(comment, "Text")
                comment_date = getattr(comment, "CreationDate")

                # Get the regex groups that the comment matches
                comment_code = find_code(comment_text)
                # Remove the found code from the comment and run the regex to look for keywords after the replacement
                comment_text = self.remove_code(comment_text, comment_code)
                comment_groups = find_groups(comment_text)
                # Keep track of which edits have relevant code (EditId, Matching Code)
                relevant_code_matches = []

                # Keep track of how many edits are by the OP and how many by others
                edits_by_author = 0
                edits_by_others = 0

                # The answer is the initial body of the answer
                prev_edit = answer
                # We start the index from two so it is easier to compare with the stack overflow revision page
                for edit_index, edit in enumerate(sorted_edits.itertuples(), 2):
                    edit_date = getattr(edit, "CreationDate")
                    # Only look at the edit if it occurred after the comment
                    if comment_date < edit_date:
                        has_edits = True

                        # Keep a counter of which authors make an edit
                        if getattr(edit, "UserName") == answer_author:
                            edits_by_author += 1
                        else:
                            edits_by_others += 1

                        prev_edit_groups = find_groups(getattr(prev_edit, "Text"))
                        edit_groups = find_groups(getattr(edit, "Text"))
                        # Determine if the edit has the same groups as the comment
                        matches = (comment_code | comment_groups) & (edit_groups ^ prev_edit_groups)
                        if len(matches) > 0:
                            total_updates += 1
                            edit_id = getattr(edit, "EventId")
                            edit_updates[edit_id] += 1
                            relevant_code_matches.append((edit_id, matches))
                    prev_edit = edit

                # Check all previous commenters to see if they have a match with the found mention
                user_mentions = find_mentions(comment_text)
                if len(user_mentions) > 0:
                    for mentioned_user in user_mentions:
                        # TODO: Will find matches with previous comments by same user as well even if already addressed
                        # ie. User1, User2, User1, User3, User4. This will match User4 to both instances of User1,
                        # even if it was only addressing the second instance
                        for prev_author, count in comment_authors.items():
                            # Remove the '@' in front of the name
                            if mentioned_user[1:] == prev_author:
                                comment_replies.append((mentioned_user, comment_author))
                # Handle the case where the OP makes a comment but not in reference to someone else
                elif comment_author == answer_author:
                    comment_replies.append(("N/A", comment_author))

                # Combine the comment code and keywords found
                comment_groups = comment_groups | comment_code
                stats.append([answer_id,
                              getattr(comment, "EventId"),
                              answer_author,
                              comment_author,
                              comment_index,
                              comment_date,
                              getattr(comment, "Score"),
                              getattr(comment, "Text"),
                              comment_groups if len(comment_groups) > 0 else "",
                              has_edits,
                              relevant_code_matches if len(relevant_code_matches) > 0 else "",
                              edits_by_author,
                              edits_by_others,
                              comment_replies if len(comment_replies) > 0 else ""])

        with open("results.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["AnswerId",
                             "CommentId",
                             "AnswerAuthor",
                             "CommentAuthor",
                             "CommentIndex",
                             "CommentDate",
                             "Comment Score",
                             "Comment",
                             "Comment Groups",
                             "Has edits after",
                             "Edit Groups (EditId, Matched Groups)",
                             "Edits by author",
                             "Edits by others",
                             "Comment mentions/replies (mentioned user, comment author)"])
            writer.writerows(stats)

        edits_dist = defaultdict(int)
        for value in answer_edits.values():
            edits_dist[value] += 1
        fig, ax = plt.subplots()
        ax.set_title("Num of answers per num of edits")
        ax.set_ylabel("Number of answers")
        ax.set_xlabel("Number of edits")
        ax.bar(list(edits_dist.keys()), edits_dist.values(), 0.5, color='g')
        # plt.show()
        plt.savefig('AnswersPerEdit.png')
        total = 0
        for value in edit_updates.values():
            total += value
        file = open("stats.txt", "w")
        file.write("Total answers analyzed: " + str(total_answers) + "\n")
        file.write("Total comments analyzed: " + str(total_comments) + "\n")
        file.write("Total comments marked as Update: " + str(total_updates) + "\n")
        file.write("Average number of comments per edit: "
                   + str(total/len(edit_updates.keys()) if len(edit_updates.keys()) > 0 else "0"))
        file.close()

    @staticmethod
    def remove_code(text, patterns):
        for pattern in patterns:
            text = text.replace("`" + pattern + "`", "")
            text = text.replace("<code>" + pattern + "</code>", "")
        return text

    def process_answers(self, answer_id):
        print("answer id:", answer_id)
        comments = self.comments.loc[self.comments['PostId'] == answer_id]

        print("Comments", comments)

        edits = self.edits.loc[self.edits['PostId'] == answer_id]
        print("Edits", edits)

        if len(edits) == 0:
            return None

        bucket = self.process_comments(answer_id, edits, comments)
        return bucket

    def process_comments(self, answer_id, edits, comments):

        bucket = {
            "answer_id": str(answer_id),
            "edits": []
        }
        return bucket

    def post_process(self):
        return

    def stats(self):
        tags = get_tags()
        for tag in tags:
            pass
