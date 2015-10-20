import unittest
import lsapi
from mock import patch
from tests.mocks.ls_socket import SocketMocks
import urllib


class LsapiDowntimesTestCase(unittest.TestCase):
    version = 'v1'
    testdowntime = 'test_downtime_service_name'
    downtime_filter_correct = '{"eq":["service_display_name","%s"]}' % testdowntime
    downtime_filter_incorrect = '{"bad":['
    downtime_filter_wrong_operator = '{"nex":["service_display_name","%s"]}' % testdowntime
    downtime_columns_correct = '["display_name", "address"]'
    downtime_columns_incorrect = '["learn_to_write_json'
    downtime_columns_not_a_list = '{"cols":["display_name", "address"]}'

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    # /downtimes GET endpoint without parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get(self):
        response = self.app.get('%s/downtimes' % self.version)
        assert response.status_code == 200
        assert self.testdowntime in response.data

    # /downtimes GET endpoint with a correct filter parameter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_correct_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_filter_correct)
        response = self.app.get('%s/downtimes?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testdowntime in response.data

    # /downtimes GET endpoint with an incorrect filter parameter (faulty json)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_faulty_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_filter_incorrect)
        response = self.app.get('%s/downtimes?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "filter parameter can't be parsed as json" in response.data

    # /downtimes GET endpoint with an incorrect filter parameter (unknown operator)
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_unknown_filter_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_filter_wrong_operator)
        response = self.app.get('%s/downtimes?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "wrong bool filter" in response.data

    # /downtimes GET endpoint with a correct columns parameter
    # livestatus decides, which columns are returned, so in a mocked world, we don't see any difference
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_correct_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_columns_correct)
        response = self.app.get('%s/downtimes?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert self.testdowntime in response.data

    # /downtimes GET endpoint with a incorrect columns parameter (faulty json)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_incorrect_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_columns_incorrect)
        response = self.app.get('%s/downtimes?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "cannot parse columns parameter" in response.data

    # /downtimes GET endpoint with a incorrect columns parameter (not resulting in list)
    # should return 400/BAD_REQUEST
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_get_with_non_list_columns_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_columns_not_a_list)
        response = self.app.get('%s/downtimes?columns=%s' % (self.version, get_parameter))
        assert response.status_code == 400
        assert "can't convert parameter columns to a list" in response.data

    # /downtimes DELETE endpoint without filter. Should return 400/BAD_REQUEST
    # since a filter parameter is mandatory
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_delete_without_parameter(self):
        response = self.app.delete('%s/downtimes' % self.version)
        assert response.status_code == 400
        assert "no filter given, not deleting all downtimes" in response.data

    # /downtimes DELETE endpoint with correct filter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_delete_with_parameter(self):
        get_parameter = urllib.quote_plus('%s' % self.downtime_filter_correct)
        response = self.app.delete('%s/downtimes?filter=%s' % (self.version, get_parameter))
        assert response.status_code == 200
        assert "DEL_SVC_DOWNTIME" in response.data
        assert "DEL_HOST_DOWNTIME" in response.data

    # /downtimes/{id} GET endpoint
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_id_get(self):
        # not really verifying the output, since it depends on a filtered livestatus output, which isn't
        # handled by this app itself but by livestatus. We're using a mocked livestatus response
        response = self.app.get('%s/downtimes/%d' % (self.version, 22222))
        assert response.status_code == 200
        assert self.testdowntime in response.data

    # /downtimes/{id} DELETE endpoint without filter
    @patch('lsapi.ls_query.ls_accessor', new=SocketMocks('lsquery mock'))
    def test_downtimes_id_delete(self):
        response = self.app.delete('%s/downtimes/%d' % (self.version, 22222))
        assert response.status_code == 200
        assert "DEL_SVC_DOWNTIME" in response.data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()