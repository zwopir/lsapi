import unittest
import urllib

from mock import patch

from lsapi import lsapi
from tests.mocks.ls_socket import SocketMocks


class LsapiServicesTestCase(unittest.TestCase):
    version = 'v1'
    testhost = 'host-aut-1af.example.com'
    testservice = 'CPU load'
    service_filter_correct = '{"eq":["display_name","%s"]}' % testservice
    service_filter_incorrect = '{"bad":['
    service_filter_wrong_operator = '{"nex":["display_name","%s"]}' % testhost
    service_columns_correct = '["display_name", "state"]'
    service_columns_incorrect = '["learn_to_write_json'
    service_columns_not_a_list = '{"cols":["display_name", "address"]}'
    downtime_data = '''{
        "downtime": {
            "start_time": 1757940301,
            "end_time": 1789476309,
            "author": "coelmueller",
            "comment": "a test downtime"
        }
    }'''
    downtime_data_incorrect_json = '''{"learn_to_write_json:
        "foo": 1,
        []
    '''
    downtime_data_missing_values = '''{
        "downtime": {
            "start_time": 1757940301,
            "author": "coelmueller",
            "comment": "a test downtime"
        }
    }'''
    downtime_data_missing_key = '{"some": "json"}'

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /services GET endpoint without parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get(self):
        response = self.app.get('%s/services' % self.version)
        assert response.status_code == 200
        assert self.testservice in response.data

    # /services GET endpoint with a correct filter parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_correct_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_correct)
        response = self.app.get('%s/services?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testservice in response.data
    
    # /services GET endpoint with an incorrect filter parameter (faulty json)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_faulty_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_incorrect)
        response = self.app.get('%s/services?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "filter parameter can't be parsed as json" in response.data
    
    # /services GET endpoint with an incorrect filter parameter (unknown operator)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_unknown_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_wrong_operator)
        response = self.app.get('%s/services?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "wrong bool filter" in response.data
    
    # /services GET endpoint with a correct columns parameter
    # livestatus decides, which columns are returned, so in a mocked world, we don't see any difference
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_correct_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_columns_correct)
        response = self.app.get('%s/services?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testservice in response.data
    
    # /hosts GET endpoint with a incorrect columns parameter (faulty json)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_incorrect_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_columns_incorrect)
        response = self.app.get('%s/services?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "cannot parse columns parameter" in response.data
    
    # /services GET endpoint with a incorrect columns parameter (not resulting in list)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_get_with_non_list_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.service_columns_not_a_list)
        response = self.app.get('%s/services?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "can't convert parameter columns to a list" in response.data
    
    # /services POST endpoint without parameter. Should return 400/BAD_REQUEST, since a filter parameter is required
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_post(self):
        response = self.app.post('%s/services' % self.version, data=self.downtime_data)
        assert response.status_code == 400
        assert "no filter given, not setting downtime on all services" in response.data

    # /services POST endpoint with parameter, but faulty post data (incorrect json)
    # Should return 400/BAD_REQUEST,
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_post_incorrect_downtime_data(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_correct)
        response = self.app.post('%s/services?filter=%s' % (self.version, get_parameter),
                                 data=self.downtime_data_incorrect_json)
        # print response.status_code
        assert response.status_code == 400
        assert "bad request" in response.data

    # /services POST endpoint with parameter, but faulty post data (missing parameter)
    # Should return 400/BAD_REQUEST,
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_post_missing_downtime_data_element(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_correct)
        response = self.app.post('%s/services?filter=%s' % (self.version, get_parameter),
                                 data=self.downtime_data_missing_values)
        assert response.status_code == 400
        assert "not all mandatory downtime parameters are given" in response.data

    # /services POST endpoint with parameter, but faulty post data (missing parameter)
    # Should return 400/BAD_REQUEST,
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_post_missing_downtime_data_key(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_correct)
        response = self.app.post('%s/services?filter=%s' % (self.version, get_parameter),
                                 data=self.downtime_data_missing_key)
        assert response.status_code == 400
        assert "POST json data doesnt include a downtime key" in response.data

    # /services POST endpoint with parameter. Should return 500/INTERNAL_SERVER_ERROR,
    # with message: "downtimes not found within 5 seconds"
    # thats ok, because we actually don't set any downtime
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_post(self):
        get_parameter = urllib.quote_plus('%s' % self.service_filter_correct)
        response = self.app.post('%s/services?filter=%s' % (self.version, get_parameter), data=self.downtime_data)
        assert response.status_code == 500
        assert "downtimes not found within 5 seconds" in response.data
    
    # /services/{hostname} GET endpoint
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_hostename_get(self):
        # not really verifying the output, since it depends on a filtered livestatus output, which isn't
        # handled by this app itself but by livestatus. We're using a mocked livestatus response
        response = self.app.get('%s/services/%s' % (self.version, self.testhost))
        assert response.status_code == 200
        assert self.testservice in response.data

    # /services/{hostname}/{servicename} GET endpoint
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_services_hostname_servicename_get(self):
        # not really verifying the output, since it depends on a filtered livestatus output, which isn't
        # handled by this app itself but by livestatus. We're using a mocked livestatus response
        response = self.app.get('%s/services/%s/%s' % (self.version,
                                                       self.testhost,
                                                       self.testservice))
        assert response.status_code == 200
        assert self.testservice in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()