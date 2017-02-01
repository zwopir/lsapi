import unittest
from nose.tools import raises, assert_equals, nottest

from tests.helpers import get_fixture_path

from lsapi.configuration.socket import (SocketConfiguration, ParsingError)


class LsApiSocketConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.invalid_config_parsingerror_path = \
            get_fixture_path('invalid-config-parsingerror.cfg')
        self.valid_config_path = get_fixture_path('valid-config.cfg')
        self.empty_config_path = get_fixture_path('empty-config.cfg')
        self.incomplete_config_path = get_fixture_path('incomplete-config.cfg')
        self.invalid_config_invalid_type_path = \
            get_fixture_path('invalid-config-invalid-type.cfg')

    def test_configfile_does_not_exist(self):
        sc = SocketConfiguration(cfg_file='bubu')
        self.assert_defaults(sc)

    @raises(ParsingError)
    def test_invalid_config(self):
        SocketConfiguration(cfg_file=self.invalid_config_parsingerror_path)

    def test_empty_config(self):
        sc = SocketConfiguration(cfg_file=self.empty_config_path)
        self.assert_defaults(sc)

    @raises(TypeError)
    def test_wrong_connection_type(self):
        SocketConfiguration(cfg_file=self.invalid_config_invalid_type_path)

    def test_valid_config(self):
        sc = SocketConfiguration(cfg_file=self.valid_config_path)
        assert_equals(2222, sc.connection_port)
        assert_equals('AF_UNIX', sc.connection_type)
        assert_equals('my.example.com', sc.connection_host)

    def test_config_fallback_defaults(self):
        sc = SocketConfiguration(cfg_file=self.incomplete_config_path)
        self.assert_defaults(sc)

    @nottest
    def assert_defaults(self, sc):
        assert_equals(sc.defaults['socketfile'], sc.connection_file)
        assert_equals(int(sc.defaults['port']), sc.connection_port)
        assert_equals(sc.defaults['host'], sc.connection_host)
        assert_equals(sc.defaults['type'], sc.connection_type)
