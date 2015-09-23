__author__ = 'oelmuellerc'
import unittest
import lsapi
import json
from mock import patch
from ls_socket_mocks import LsSocketMocks




class LsapiTestCase(unittest.TestCase):
    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    @patch('lsapi.ls_socket_reader', new=LsSocketMocks('connection_parameter'))
    def test_hosts_get(self):
        response = self.app.get('api/hosts')

        self.assertRegexpMatches(response.data, 'dp1aut1af.log.epd.epost.noris.de')

    def test_hosts_post(self):
        pass

    def test_host_hostname(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()