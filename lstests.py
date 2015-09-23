#!/usr/bin/python
#
import socket
import csv
import json

socket_path = "/var/lib/nagios/rw/live"
socket_addr = '127.0.0.1'
socket_port = 6557
use_unix_socket = False
ls_format_query = "\nOutputFormat: csv\nResponseHeader: fixed16\n"
#ls_format_query = "\nOutputFormat: csv\n"
# default output columns for livestatus tables
default_columns = {}
default_columns["hosts"] = ["acknowledged", "address", "comments", "display_name", "downtimes", "last_state", "last_hard_state"]
default_columns["services"] = ["acknowledged", "comments", "description", "display_name", "host_display_name", "last_state", "last_hard_state"]
default_columns["downtimes"] = ["author", "comment", "duration", "end_time", "entry_time", "fixed", "host_display_name", "service_display_name"]
default_columns["hosta"] = ["acknowledged", "address", "comments", "display_name", "downtimes", "last_state", "last_hard_state"]




# unix socket = AF_UNIX, tcp socket = AF_INET
if use_unix_socket:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_path)
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket_addr, socket_port))

# Write command to socket
entity = 'services'

columns = default_columns[entity]
columns_s = ' '.join(columns)
query = "GET " + entity + "\nColumns:" + columns_s + ls_format_query
s.send(query)

# Important: Close sending direction. That way
# the other side knows we are finished.
s.shutdown(socket.SHUT_WR)

# Now read the answer
socket_as_file = s.makefile()

header = socket_as_file.read(16)
ls_statuscode = int(header[0:3])
if ls_statuscode != 200:
    status = socket_as_file.readline()
    print status
else:
    data = [row for row in csv.DictReader(socket_as_file, fieldnames=columns, delimiter=';')]
    print json.dumps(data)
