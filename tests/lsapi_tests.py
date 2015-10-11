import unittest
import lsapi
#from nose.tools import assert_equal
from mock import patch
from tests.mocks.ls_socket import LsSocketMocks


class LsapiTestCase(unittest.TestCase):
    version = 'v1'
    testhost = 'host-aut-1af.example.com'
    host_filter_correct = '{"eq":["display_name","%s"]}' % testhost
    host_filter_incorrect = '{"bad":['

    def setUp(self):
        lsapi.app.config['TESTING'] = True
        self.app = lsapi.app.test_client()

    @patch('lsapi.ls_query.ls_accessor', new=LsSocketMocks('foo'))
    def test_hosts_get(self):
        response = self.app.get('%s/hosts' % self.version)
        print response.data
        assert True

    # API endpoints
    #@patch('lsapi.SocketConfiguration')
    #def test_hosts_get(self, mock):
    #    print str(mock)
    #    mock.return_value = 'foo'
    #    response = self.app.get('%s/hosts' % self.version)
    #    print str(response.data)
    #    assert True

#   def test_hosts_get_with_correct_filter_parameter(self):
#       # TODO: pass parameter
#       response = self.app.get('%s/hosts' % self.version)
#       assert self.testhost in response.data
#
#   def test_hosts_get_with_faulty_filter_parameter(self):
#       # TODO: pass parameter
#       response = self.app.get('%s/hosts' % self.version)
#       assert self.testhost in response.data
#
#   def test_hosts_hostname_get(self):
#       # not really verifying the output, since it depends on a filtered livestatus output, which isn't
#       # handled by this app itself but by livestatus
#       response = self.app.get('%s/hosts/%s' % (self.version, self.testhost))
#       assert self.testhost in response.data
#
#   def test_hosts_hostname(self):
#       pass
#
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()