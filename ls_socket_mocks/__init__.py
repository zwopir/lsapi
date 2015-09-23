__author__ = 'oelmuellerc'
import json
import os


class LsSocketMocks:

    def __init__(self, connection_parameter, socket_type='AF_INET'):
        self.socket_type = socket_type
        self.ls_reader_object = None
        self.connection_parameter = connection_parameter

    def connect(self):
        self.ls_reader_object = None

    def send_query(self, query_object):
        pass

    def send_command(self, command):
        pass

    def read_query_result(self, query_object):
        """
            return ready to consume json structures depending on query_object's
            entity instance variable
        """
        datafile = os.path.dirname(__file__) + '/../fixtures/' + query_object.entity + '.json'

        with open(datafile) as host_data_file:
            return_data = json.load(host_data_file)
        return (200, return_data)
