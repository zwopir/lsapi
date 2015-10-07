import csv
import socket

from api_exceptions import LivestatusSocketException
from model.lsquery import LsQuery


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
        if isinstance(query_object, LsQuery):
            # query object
            s = self.sock
            s.send(query_object.querystring)
            s.shutdown(socket.SHUT_WR)
            self.ls_reader_object = s.makefile()
        elif isinstance(query_object, basestring):
            s = self.sock
            s.send(query_object)
            s.shutdown(socket.SHUT_WR)
            self.ls_reader_object = s.makefile()
        else:
            raise LivestatusSocketException("livestatus query must be a string or LsQuery instance",
                                            status_code=500)

    def read_query_result(self, query_object):
        # TODO: remove LsQuery usage if not longer needed
        if isinstance(query_object, LsQuery):
            fields = query_object.fields
        else:
            fields = query_object
        # read header information
        header = self.ls_reader_object.read(16)
        ls_statuscode = int(header[0:3])
        if ls_statuscode != 200:
            status = self.ls_reader_object.readline()
            return ls_statuscode, status
        else:
            data = [row for row in csv.DictReader(self.ls_reader_object,
                                                  fieldnames=fields,
                                                  delimiter=';')]
            if len(data) < 1:
                return 404, "no data returned"
            else:
                return (ls_statuscode, data)