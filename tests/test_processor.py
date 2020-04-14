import ast
import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath('../src'))

from processor import Processor


@pytest.fixture
def processor(request):
    df_answers = pd.read_csv("tests/files/" + request.param + "/" + request.param + "_answers.csv",
                             parse_dates=["CreationDate"])
    df_comments = pd.read_csv("tests/files/" + request.param + "/" + request.param + "_comments.csv",
                              parse_dates=["CreationDate"])
    df_edits = pd.read_csv("tests/files/" + request.param + "/" + request.param + "_edits.csv",
                           parse_dates=["CreationDate"])
    return Processor(df_answers, df_comments, df_edits), request.param


class TestCases:
    @pytest.mark.parametrize("processor", ["16184827",
                                           "44880776",
                                           "35666",
                                           "25915251",
                                           "33507565",
                                           "9554482",
                                           "21616398",
                                           "24810414",
                                           "24947520",
                                           "44187121"], indirect=True)
    def test_validity(self, processor):
        processor[0].process()

        stored_stats = open("tests/files/" + processor[1] + "/" + processor[1] + "_stats.txt", "r")
        for line in stored_stats.readlines():
            if line.split(": ")[0] == "Total comments marked as Update":
                assert ast.literal_eval(line.split(": ")[1]) == processor.total_marked_updates

        calculated_results = pd.DataFrame(processor[0].stats,
                                          columns=["AnswerId",
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

        stored_results = pd.read_csv("tests/files/" + processor[1] + "/" + processor[1] + "_results.csv",
                                     parse_dates=["CommentDate"], na_filter=False)
        calculated_groups = calculated_results[["Edit Groups (EditId, Matched Groups)"]]
        stored_groups = stored_results[["Edit Groups (EditId, Matched Groups)"]]
        for calculated_list, stored_list in zip(calculated_groups.values.tolist(), stored_groups.values.tolist()):
            for calculated_group, stored_group in zip(calculated_list, stored_list):
                assert calculated_group == stored_group or (calculated_group == ast.literal_eval(stored_group))
