from __future__ import print_function

import os
from ConfigParser import (SafeConfigParser, ParsingError,
                          NoSectionError, NoOptionError)


class SocketConfiguration(object):
    defaults = {
        'type': 'AF_INET',
        'host': 'localhost',
        'socketfile': '/omd/sites/monitoring/tmp/run/live',
        # must be string to make SafeConfigParser.getint happy
        'port': '6557'
    }

    def __init__(self, cfg_file='lsapi.cfg'):
        config = SafeConfigParser(defaults=self.defaults)
        if os.path.exists(cfg_file):
            try:
                config.read(cfg_file)
            except (ParsingError, NoSectionError):
                raise
        else:
            print("Path {path} does not exist, falling back to defaults: "
                  "{defaults}.".format(path=cfg_file, defaults=self.defaults))

        if not config.has_section('connection'):
            config.add_section('connection')

        self.connection_type = config.get(section='connection',
                                          option='type')
        self.connection_host = config.get(section='connection',
                                          option='host')
        self.connection_file = config.get(section='connection',
                                          option='socketfile')
        self.connection_port = config.getint(section='connection',
                                             option='port')

        if self.connection_type == 'AF_INET':
            self.connection_string = (self.connection_host, self.connection_port)
        elif self.connection_type == 'AF_UNIX':
            self.connection_string = self.connection_file
        else:
            raise TypeError("connection type must be either AF_INET or AF_UNIX")
