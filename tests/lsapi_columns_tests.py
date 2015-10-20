import unittest
import urllib

from mock import patch

from lsapi import lsapi
from tests.mocks.ls_socket import SocketMocks


class LsapiColumnsTestCase(unittest.TestCase):
    version = 'v1'
    testcolumn = "A description of the column"
    column_filter_correct = '{"eq":["description","%s"]}' % testcolumn
    column_filter_incorrect = '{"bad":['
    column_filter_wrong_operator = '{"nex":["description","%s"]}' % testcolumn
    column_columns_correct = '["description", "name"]'
    column_columns_incorrect = '["learn_to_write_json'
    column_columns_not_a_list = '{"cols":["name", "description"]}'

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /columns GET endpoint without parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get(self):
        response = self.app.get('%s/columns' % self.version)
        assert response.status_code == 200
        assert self.testcolumn in response.data

    # /columns GET endpoint with a correct filter parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_correct_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_filter_correct)
        response = self.app.get('%s/columns?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testcolumn in response.data

    # /columns GET endpoint with an incorrect filter parameter (faulty json)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_faulty_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_filter_incorrect)
        response = self.app.get('%s/columns?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "filter parameter can't be parsed as json" in response.data

    # /columns GET endpoint with an incorrect filter parameter (unknown operator)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_unknown_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_filter_wrong_operator)
        response = self.app.get('%s/columns?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "wrong bool filter" in response.data

    # /columns GET endpoint with a correct columns parameter
    # livestatus decides, which columns are returned, so in a mocked world, we don't see any difference
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_correct_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_columns_correct)
        response = self.app.get('%s/columns?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testcolumn in response.data

    # /columns GET endpoint with a incorrect columns parameter (faulty json)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_incorrect_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_columns_incorrect)
        response = self.app.get('%s/columns?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "cannot parse columns parameter" in response.data

    # /columns GET endpoint with a incorrect columns parameter (not resulting in list)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_columns_get_with_non_list_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.column_columns_not_a_list)
        response = self.app.get('%s/columns?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "can't convert parameter columns to a list" in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()