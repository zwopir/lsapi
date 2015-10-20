import csv
import socket
from helper.api_exceptions import LivestatusSocketException


class Socket:
    """
    """
    def __init__(self, connection_parameter, socket_type='AF_INET'):
        self.socket_type = socket_type
        self.ls_reader_object = None
        self.connection_parameter = connection_parameter
        self.sock = None

    def connect(self):
        try:
            if self.socket_type == 'AF_INET':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.connection_parameter)

            elif self.socket_type == 'AF_UNIX':
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(self.connection_parameter)
            else:
                raise LivestatusSocketException("no valid socket_type given: %s" %
                                                self.socket_type,
                                                status_code=500)
            self.sock = sock
        except:
            raise LivestatusSocketException("can't connect to Livestatus %s" %
                                            str(self.connection_parameter),
                                            status_code=500)
        # there is nothing to read yet
        self.ls_reader_object = None

    def disconnect(self):
        if self.sock is not None:
            self.sock.close()

    def send(self, query_object):
        # query object
        s = self.sock
        s.send(query_object.querystring)
        s.shutdown(socket.SHUT_WR)
        self.ls_reader_object = s.makefile()

    def read_query_result(self, query_object):
        """
        read from Livestatus Socket
        :param query_object: LsQuery instance or List of fields to be returned in output dict
        :return (returncode, data)
        :type tuple(int, dict)
        """
        fields = query_object.fields
        header = self.ls_reader_object.read(16)
        # livestatus returns HTTPish status codes
        ls_statuscode = int(header[0:3])
        if ls_statuscode != 200:
            status = self.ls_reader_object.readline()
            return ls_statuscode, status
        else:
            # return data as dict. Livestatus' JSON output is unusable (data without keys)
            data = [row for row in csv.DictReader(self.ls_reader_object,
                                                  fieldnames=fields,
                                                  delimiter=';')]
            if len(data) < 1:
                return 404, "no data returned"
            else:
                return (ls_statuscode, data)