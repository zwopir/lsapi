import json
import os


class SocketMocks:

    def __init__(self, connection_parameter, socket_type='AF_INET'):
        self.socket_type = socket_type
        self.ls_reader_object = None
        self.connection_parameter = connection_parameter

    def connect(self):
        pass

    def send(self, query_object):
        pass

    def read_query_result(self, query_object):
        """
            return ready to consume dict structures depending on query_object's
            entity instance variable
            :param LsQuery object
            :return (returncode, data)
            :type tuple(int, dict)
        """
        if "GET %s\nStats" % query_object.entity in query_object.querystring:
            prefix = 'stats_'
        else:
            prefix = ''

        datafile = os.path.dirname(__file__) + '/../fixtures/' + prefix + query_object.entity + '.json'
        with open(datafile) as data_file:
            return_data = json.load(data_file)
        return 200, return_data

    def disconnect(self):
        pass