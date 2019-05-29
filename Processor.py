import multiprocessing as mp


def get_tags():
    with open("tags.cnf") as f:
        tags = f.read().splitlines()

    return tags


class Processor:

    def __init__(self, answers, comments, edits):
        self.answers = answers
        self.comments = comments
        self.edits = edits

        self.dataset = []

    def process(self):
        pool = mp.Pool(mp.cpu_count() - 1)

    def post_process(self):
        pass

    def stats(self):
        tags = get_tags()
        for tag in tags:
            print(tag)
