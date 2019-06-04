import multiprocessing as mp
import pickle


def get_tags():
    with open("tags.cfg") as f:
        tags = f.read().splitlines()

    return tags


class Processor:

    def __init__(self, df_answers, df_comments, df_edits):
        self.answers = df_answers
        self.comments = df_comments
        self.edits = df_edits

        self.dataset = []

    def process(self):
        pool = mp.Pool(mp.cpu_count() - 1)
        answer_ids = list(self.answers["AnswerId"])
        buckets = pool.map(self.process_answers, answer_ids)
        pool.close()
        pool.join()
        self.dataset = [b for b in buckets if b is not None]
        with open('dataset.pickle', 'wb') as file:
            pickle.dump(self.dataset, file)

    def process_answers(self, answer_id):
        comments = self.comments.loc[self.comments['PostId'] == answer_id]
        edits = self.edits.loc[self.edits['PostId'] == answer_id]

        if len(edits) == 0:
            return None

        bucket = self.process_edits(answer_id, edits, comments)
        return bucket

    def post_process(self):
        return

    def stats(self):
        tags = get_tags()
        for tag in tags:
            print(tag)

    def process_edits(self, answer_id, edits, comments):
        bucket = {
            "answer_id": str(answer_id),
            "edits": []
        }
        return bucket
