from ConfigParser import ConfigParser
from model.socket_communication import LsSocket
import os
import sys


class SocketConfiguration:
    def __init__(self, reference_file, filename='lsapi.cfg'):
        # read and parse configuration file
        config = ConfigParser()
        this_path = os.path.dirname(reference_file) + '/'
        this_path_conf = os.path.dirname(reference_file) + '/conf/'
        for path in ['/etc/', this_path, this_path_conf]:
            if os.path.exists(path + filename):
                config.read(path + filename)
                break

        self.connection_type = config.get('connection', 'type', 'AF_INET')
        self.connection_host = config.get('connection', 'host', 'localhost')
        self.connection_port = int(config.get('connection', 'port', 6557))
        self.connection_file = config.get('connection', 'socketfile', '/omd/sites/monitoring/tmp/run/live')
        # get connection string
        if self.connection_type == 'AF_INET':
            self.connection_string = (self.connection_host, self.connection_port)
            # self.ls_accessor = LsSocket((self.connection_host, self.connection_port), self.connection_type)
        elif self.connection_type == 'AF_UNIX':
            self.connection_string = self.connection_file
            # self.ls_accessor = LsSocket(self.connection_file, self.connection_type)
        else:
            raise SystemExit("connection type must be either AF_INET or AF_UNIX")