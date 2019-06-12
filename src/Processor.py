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

        # print("total number of answers", len(answer_ids))
        # print("total number of comments", len(list(self.comments["POST_ID"])))
        # print("total number of edits", len(list(self.edits["POST_ID"])))

        for answer in self.answers.itertuples():
            # Get the author of the answer
            answer_author = getattr(answer, "UserName")
            answer_id = getattr(answer, "PostId")

            comments = self.comments.loc[self.comments["PostId"] == answer_id]
            edits = self.edits.loc[self.edits["PostId"] == answer_id]

            # TODO: Stats should be: CommentId, has_code, has_updates, has_relevant_code, comment_groups, edit_authors
            stats = dict()

            # TODO: Keep track of comment and edit authors
            # We want to preserve the ordering on the comments we see
            comment_authors = OrderedDict()

            for comment in comments.itertuples():
                has_code = False
                has_edits = False
                has_relevant_code = False

                # TODO: Keep track of comment authors and their position
                comment_author = getattr(comment, "UserName")
                if comment_author in comment_authors:
                    comment_authors[comment_author] += 1
                else:
                    comment_authors[comment_author] = 1

                # We do not need to preserve the ordering on the edits we see
                edit_authors = defaultdict(int)

                comment_text = getattr(comment, "Text")
                comment_date = getattr(comment, "CreationDate")

                comment_groups = find_groups(comment_text)
                if len(comment_groups) > 0:
                    has_code = True

                for edit in edits.itertuples():
                    edit_text = getattr(edit, "Text")
                    edit_date = getattr(edit, "CreationDate")
                    # Only look at the edit if it occurred after the comment
                    if comment_date < edit_date:
                        has_edits = True

                        # Keep a counter of which authors make an edit
                        edit_authors[getattr(edit, "UserName")] += 1

                        # Determine if the edit has the same groups as the comment
                        edit_groups = find_groups(edit_text)
                        matches = comment_groups & edit_groups
                        # print(comment_groups)
                        # print(edit_groups)
                        # print(matches)
                        if len(matches) > 1:
                            has_relevant_code = True
                        #break
                edits_by_author = 0
                edits_by_others = 0
                for author, count in edit_authors.items():
                    if author == answer_author:
                        edits_by_author += 1
                    else:
                        edits_by_others += 1

                print("edits by author: %i, edits by others: %i" % (edits_by_author, edits_by_others))

                # TODO: Check all previous commenters to see if they have a match with the found mention
                # user_mention = find_mentions(comment_text)
                # if user_mention is not None:
                #     user = user_mention.expand("\1")
                #     if len(user) > 0:
                #         if user == comment_author:
                #             increment counter
                print("Has code: %r, Has edits after: %r, Edit has relevant code: %r" % (has_code, has_edits, has_relevant_code))
                #break

            answer_author_positions = []
            for index, (author, count) in enumerate(comment_authors.items()):
                if author == answer_author:
                    answer_author_positions.append(index)

            print(answer_author_positions)
            break

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
            print(tag)
