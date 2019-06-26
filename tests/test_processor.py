import pytest
import pandas as pd

from processor import Processor


@pytest.fixture
def processor(request):
    df_answers = pd.read_csv("tests/files/" + request.param + "_answers.csv", parse_dates=["CreationDate"])
    df_comments = pd.read_csv("tests/files/" + request.param + "_comments.csv", parse_dates=["CreationDate"])
    df_edits = pd.read_csv("tests/files/" + request.param + "_edits.csv", parse_dates=["CreationDate"])
    print(df_answers)
    print(df_edits)
    print(df_comments)
    return Processor(df_answers, df_comments, df_edits)


class TestCases:

    @pytest.mark.parametrize('processor', ['21616398'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test_7(self, processor):
        processor.process()
        assert processor.total_marked_updates == 4
