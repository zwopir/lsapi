import csv
import socket
from api_exceptions import LivestatusSocketException
from lsquery import LsQuery

__author__ = 'oelmuellerc'


class LsSocket:
    """
    """
    def __init__(self, connection_parameter, socket_type='AF_INET'):
        self.socket_type = socket_type
        self.ls_reader_object = None
        self.connection_parameter = connection_parameter
        self.sock = None

    def connect(self):
        if self.socket_type == 'AF_INET':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.connection_parameter)
        elif self.socket_type == 'AF_UNIX':
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.connection_parameter)
        else:
            raise LivestatusSocketException("no valid socket_type given: %s" % self.socket_type, status_code=500)
        self.sock = sock
        # there is nothing to read yet
        self.ls_reader_object = None

    def send_query(self, query_object):
        if isinstance(query_object, LsQuery):
            if self.socket_type in ['AF_INET', 'AF_UNIX']:
                s = self.sock
                s.send(query_object.query)
                s.shutdown(socket.SHUT_WR)
                self.ls_reader_object = s.makefile()
        else:
            raise LivestatusSocketException("sending livestatus query failed", status_code=500)

    def send_command(self, command):
        if self.socket_type in ['AF_INET', 'AF_UNIX']:
            s = self.sock
            s.send(command)
            s.shutdown(socket.SHUT_WR)

    def read_query_result(self, query_object):
        if isinstance(query_object, LsQuery):
            # read header information
            header = self.ls_reader_object.read(16)
            ls_statuscode = int(header[0:3])
            if ls_statuscode != 200:
                status = self.ls_reader_object.readline()
                return (ls_statuscode, status)
            else:
                data = [row for row in csv.DictReader(self.ls_reader_object, fieldnames=query_object.fields, delimiter=';')]
                if len(data) < 1:
                    return 404, "no data returned"
                else:
                    return (ls_statuscode, data)
        else:
            raise LivestatusSocketException("invalid query object given", status_code=500)