import csv
import multiprocessing as mp
import pickle

from collections import defaultdict, OrderedDict
from RegexPatterns import find_groups
from RegexPatterns import find_mentions


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
        # pool = mp.Pool(mp.cpu_count() - 1)

        # Keep track of stats to write to csv
        stats = []
        for answer in self.answers.itertuples():
            # Get the author of the answer
            answer_author = getattr(answer, "UserName")
            answer_id = getattr(answer, "PostId")

            # Retrieve all the comments and edits on this answer and sort them ascending by time
            comments = self.comments.loc[self.comments["PostId"] == answer_id]
            sorted_comments = comments.sort_values(by=['CreationDate'])
            edits = self.edits.loc[self.edits["PostId"] == answer_id]
            sorted_edits = edits.sort_values(by=['CreationDate'])

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
                comment_groups = find_groups(comment_text)

                # Keep track of which edits have relevant code (EditId, Matching Code)
                relevant_code_matches = []

                # Keep track of how many edits are by the OP and how many by others
                edits_by_author = 0
                edits_by_others = 0

                for edit in sorted_edits.itertuples():
                    edit_text = getattr(edit, "Text")
                    edit_date = getattr(edit, "CreationDate")
                    # Only look at the edit if it occurred after the comment
                    if comment_date < edit_date:
                        has_edits = True

                        # Keep a counter of which authors make an edit
                        if getattr(edit, "UserName") == answer_author:
                            edits_by_author += 1
                        else:
                            edits_by_others += 1

                        # Determine if the edit has the same groups as the comment
                        edit_groups = find_groups(edit_text)
                        matches = comment_groups & edit_groups
                        if len(matches) > 1:
                            relevant_code_matches.append((getattr(edit, "EventId"), matches))

                # Check all previous commenters to see if they have a match with the found mention
                user_mention = find_mentions(comment_text)
                if user_mention is not None:
                    mentioned_user = user_mention.group(0)[1:]
                    # Check for zero-length match
                    if len(mentioned_user) > 0:
                        # TODO: Currently this will only find mentions to ONE user,
                        # TODO: Will find matches with previous comments by same user as well even if already addressed
                        # ie. User1, User2, User1, User3, User4. This will match User4 to both instances of User1,
                        # even if it was only addressing the second instance
                        for index, (prev_author, count) in enumerate(comment_authors.items()):
                            if mentioned_user == prev_author:
                                comment_replies.append((mentioned_user, comment_author))
                # Handle the case where the OP makes a comment but not in reference to someone else
                elif comment_author == answer_author:
                    comment_replies.append(("N/A", comment_author))
                stats.append([answer_id,
                              getattr(comment, "EventId"),
                              answer_author,
                              comment_author,
                              comment_index,
                              comment_date,
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
                             "Has code",
                             "Has edits after",
                             "Edits have relevant code",
                             "Edits by author",
                             "Edits by others",
                             "Comment mentions/replies (mentioned user, comment author)"])
            writer.writerows(stats)

        # buckets = pool.map(self.process_answers, answer_ids)
        # pool.close()
        # pool.join()
        # self.dataset = [b for b in buckets if b is not None]
        # with open('dataset.pickle', 'wb') as file:
        #     pickle.dump(self.dataset, file)

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
