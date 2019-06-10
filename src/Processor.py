import multiprocessing as mp
import pickle


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
        #pool = mp.Pool(mp.cpu_count() - 1)
        answer_ids = list(self.answers["ANSWER_ID"])
        # print("total number of answers", len(answer_ids))
        # print("total number of comments", len(list(self.comments["POST_ID"])))
        # print("total number of edits", len(list(self.edits["POST_ID"])))

        for answer_id in answer_ids:
            comments = sorted(set(self.comments.loc[self.comments["POST_ID"] == answer_id]))
            print(comments)
            edits = sorted(set(self.edits.loc[self.edits["POST_ID"] == answer_id]))
            print(edits)
            for comment in comments:
                print(comment)
                for edit in edits:
                    print(edit)
                    break
                break
            break


        # buckets = pool.map(self.process_answers, answer_ids)
        # pool.close()
        # pool.join()
        # self.dataset = [b for b in buckets if b is not None]
        # with open('dataset.pickle', 'wb') as file:
        #     pickle.dump(self.dataset, file)

    def process_answers(self, answer_id):
        print("answer id:", answer_id)
        comments = self.comments.loc[self.comments['POST_ID'] == answer_id]

        print("Comments", comments)

        edits = self.edits.loc[self.edits['POST_ID'] == answer_id]
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
