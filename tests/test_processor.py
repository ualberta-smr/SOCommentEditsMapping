import pytest
import pandas as pd
import sys
sys.path.append('/smr/Projects/Python/socomments/src')

from processor import Processor


@pytest.fixture
def processor(request):
    df_answers = pd.read_csv("tests/files/" + request.param + "_answers.csv", parse_dates=["CreationDate"])
    df_comments = pd.read_csv("tests/files/" + request.param + "_comments.csv", parse_dates=["CreationDate"])
    df_edits = pd.read_csv("tests/files/" + request.param + "_edits.csv", parse_dates=["CreationDate"])
    return Processor(df_answers, df_comments, df_edits)


class TestCases:

    @pytest.mark.parametrize('processor', ['16184827'], indirect=True)
    # Test an answer with high upvotes
    def test1(self, processor):
        processor.process()
        assert processor.total_marked_updates == 1

    @pytest.mark.parametrize('processor', ['12521287'], indirect=True)
    # Test an answer with low upvotes
    def test2(self, processor):
        processor.process()
        assert processor.total_marked_updates == 0

    @pytest.mark.parametrize('processor', ['35666'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test3(self, processor):
        processor.process()
        assert processor.total_marked_updates == 2

    @pytest.mark.parametrize('processor', ['25915251'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test4(self, processor):
        processor.process()
        assert processor.total_marked_updates == 1

    @pytest.mark.parametrize('processor', ['21616398'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test5(self, processor):
        processor.process()
        assert processor.total_marked_updates == 4

    @pytest.mark.parametrize('processor', ['24810414'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test6(self, processor):
        processor.process()
        assert processor.total_marked_updates == 1

    @pytest.mark.parametrize('processor', ['24947520'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test7(self, processor):
        processor.process()
        assert processor.total_marked_updates == 2

    @pytest.mark.parametrize('processor', ['44187121'], indirect=True)
    # Test an answer with little edits and lots of comments
    def test8(self, processor):
        processor.process()
        assert processor.total_marked_updates == 1
