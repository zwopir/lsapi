import unittest
import urllib

from mock import patch

from lsapi import lsapi
from tests.mocks.ls_socket import SocketMocks


class LsapiColumnsTestCase(unittest.TestCase):
    version = 'v1'
    testcomment = "This service has been scheduled for fixed downtime"
    comment_filter_correct = '{"eq":["comment","%s"]}' % testcomment
    comment_filter_incorrect = '{"bad":['
    comment_filter_wrong_operator = '{"nex":["comment","%s"]}' % testcomment
    comment_columns_correct = '["comment", "author"]'
    comment_columns_incorrect = '["learn_to_write_json'
    comment_columns_not_a_list = '{"cols":["comment", "author"]}'

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /comments GET endpoint without parameter
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get(self):
        response = self.app.get('%s/comments' % self.version)
        assert response.status_code == 200
        assert self.testcomment in response.data

    # /comments GET endpoint with a correct filter parameter
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_correct_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_filter_correct)
        response = self.app.get('%s/comments?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testcomment in response.data

    # /comments GET endpoint with an incorrect filter parameter (faulty json)
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_faulty_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_filter_incorrect)
        response = self.app.get('%s/comments?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "filter parameter can't be parsed as json" in response.data

    # /comments GET endpoint with an incorrect filter parameter (unknown operator)
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_unknown_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_filter_wrong_operator)
        response = self.app.get('%s/comments?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "wrong bool filter" in response.data

    # /comments GET endpoint with a correct comments parameter
    # livestatus decides, which comments are returned, so in a mocked world, we don't see any difference
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_correct_comments_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_columns_correct)
        response = self.app.get('%s/comments?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testcomment in response.data

    # /comments GET endpoint with a incorrect comments parameter (faulty json)
    # should return 400/BAD_REQUEST
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_incorrect_comments_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_columns_incorrect)
        response = self.app.get('%s/comments?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "cannot parse columns parameter" in response.data

    # /comments GET endpoint with a incorrect comments parameter (not resulting in list)
    # should return 400/BAD_REQUEST
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get_with_non_list_comments_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.comment_columns_not_a_list)
        response = self.app.get('%s/comments?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "can't convert parameter columns to a list" in response.data

    # /comments/{id} GET endpoint without parameter
    @patch('lsapi.lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_comments_get(self):
        response = self.app.get('%s/comments/%d' % (self.version, 22222))
        assert response.status_code == 200
        assert self.testcomment in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
