import unittest
import lsapi
from mock import patch
from tests.mocks.ls_socket import LsSocketMocks
import urllib


class LsapiTestCase(unittest.TestCase):
    version = 'v1'
    testhost = 'host-aut-1af.example.com'
    host_filter_correct = '{"eq":["display_name","%s"]}' % testhost
    host_filter_incorrect = '{"bad":['
    host_filter_wrong_operator = '{"nex":["display_name","%s"]}' % testhost
    host_columns_correct = '["display_name", "address"]'
    host_columns_incorrect = '["learn_to_write_json'
    host_columns_not_a_list = '{"cols":["display_name", "address"]}'
    downtime_data = '''{
        "downtime": {
            "start_time": 1757940301,
            "end_time": 1789476309,
            "author": "coelmueller",
            "comment": "a test downtime"
        }
    }'''

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /hosts GET endpoint without parameter
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get(self):
        response = self.app.get('%s/hosts' % self.version)
        assert response.status_code == 200
        assert self.testhost in response.data

    # /hosts GET endpoint with a correct filter parameter
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_correct_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_filter_correct)
        response = self.app.get('%s/hosts?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testhost in response.data

    # /hosts GET endpoint with an incorrect filter parameter (faulty json)
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_faulty_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_filter_incorrect)
        response = self.app.get('%s/hosts?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "filter parameter can't be parsed as json" in response.data

    # /hosts GET endpoint with an incorrect filter parameter (unknown operator)
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_unknown_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_filter_wrong_operator)
        response = self.app.get('%s/hosts?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "wrong bool filter" in response.data

    # /hosts GET endpoint with a correct columns parameter
    # livestatus decides, which columns are returned, so in a mocked world, we don't see any difference
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_correct_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_columns_correct)
        response = self.app.get('%s/hosts?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testhost in response.data

    # /hosts GET endpoint with a incorrect columns parameter (faulty json)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_incorrect_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_columns_incorrect)
        response = self.app.get('%s/hosts?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "cannot parse columns parameter" in response.data

    # /hosts GET endpoint with a incorrect columns parameter (not resulting in list)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_get_with_non_list_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.host_columns_not_a_list)
        response = self.app.get('%s/hosts?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "can't convert parameter columns to a list" in response.data

    # /hosts POST endpoint without parameter. Should return 400/BAD_REQUEST, since a filter parameter is required
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_post(self):
        response = self.app.post('%s/hosts' % self.version, data=self.downtime_data)
        assert response.status_code == 400
        assert "no filter given, not setting downtime on all hosts" in response.data

    # /hosts POST endpoint with parameter. Should return 500/INTERNAL_SERVER_ERROR,
    # with message: "downtimes not found within 5 seconds"
    # thats ok, because we actually don't set any downtime
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    @patch('lsapi.nagios_command.ls_accessor', new=LsSocketMocks('nagios command mock'))
    def test_hosts_post(self):
        get_parameter = urllib.quote_plus('%s' % self.host_filter_correct)
        response = self.app.post('%s/hosts?filter=%s' % (self.version, get_parameter), data=self.downtime_data)
        assert response.status_code == 500
        assert "downtimes not found within 5 seconds" in response.data

    # /hosts/{hostname} GET endpoint
    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('lsquery mock'))
    def test_hosts_hostname_get(self):
        # not really verifying the output, since it depends on a filtered livestatus output, which isn't
        # handled by this app itself but by livestatus. We're using a mocked livestatus response
        response = self.app.get('%s/hosts/%s' % (self.version, self.testhost))
        assert response.status_code == 200
        assert self.testhost in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()