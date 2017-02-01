import json

from tests.helpers import get_fixture


class SocketMocks(object):
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
        path = "{prefix}{entity}.json".format(
            prefix='stats_' if "GET {entity}\nStats".format(
                entity=query_object.entity) in query_object.querystring else '',
            entity=query_object.entity)

        return 200, json.loads(get_fixture(path))

    def disconnect(self):
        pass
