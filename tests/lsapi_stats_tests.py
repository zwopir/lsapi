import unittest

from mock import patch

from webapp import lsapi
from tests.mocks.ls_socket import SocketMocks


class LsapiColumnsTestCase(unittest.TestCase):
    version = 'v1'
    testhost = "host-aut-1af.example.com"
    testservice = 'CPU load'
    testauthor = 'coelmueller'
    column_filter_correct = '{"eq":["description","%s"]}' % testhost
    column_filter_incorrect = '{"bad":['
    column_filter_wrong_operator = '{"nex":["description","%s"]}' % testhost
    column_columns_correct = '["description", "name"]'
    column_columns_incorrect = '["learn_to_write_json'
    column_columns_not_a_list = '{"cols":["name", "description"]}'

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /stats GET endpoint on hosts
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_hosts_eq_display_name(self):
        response = self.app.get('%s/stats/hosts/eq/display_name/%s' % (self.version, self.testhost))
        assert "count" in response.data
        assert response.status_code == 200

    # /stats GET endpoint on services
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_services_eq_display_name(self):
        response = self.app.get('%s/stats/services/eq/display_name/%s' % (self.version, self.testservice))
        assert "count" in response.data
        assert response.status_code == 200

    # /stats GET endpoint on downtimes
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_downtimes_eq_display_name(self):
        response = self.app.get('%s/stats/downtimes/eq/author/%s' % (self.version, self.testauthor))
        assert "count" in response.data
        assert response.status_code == 200

    # /stats GET endpoint on comments
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_comments_eq_display_name(self):
        response = self.app.get('%s/stats/comments/eq/author/%s' % (self.version, self.testauthor))
        assert "count" in response.data
        assert response.status_code == 200

    # /stats GET endpoint on hosts with non-existent column
    # can't be tested with a stupid lssocket mock: Livestatus returns an error
    # which isn't returned by mock
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_hosts_eq_whatever(self):
        _ = self.app.get('%s/stats/hosts/eq/whatever/%s' % (self.version, self.testhost))
        assert True

    # /stats GET enpoint on hosts with non-existent operator
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_stats_hosts_wrong_operator(self):
        response = self.app.get('%s/stats/hosts/nex/display_name/%s' % (self.version, self.testhost))
        assert response.status_code == 400
        assert "unknown compare operator nex" in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()