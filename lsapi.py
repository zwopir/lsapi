#!/usr/bin/env python
from __future__ import print_function
import ConfigParser
import os
import sys
import urllib
import random
import time
from flask import Flask, request, jsonify
from lssocket.socket_communication import LsSocket
from lsquery import LsQuery
from downtimes import NagiosDowntime
from api_exceptions import \
    FilterParsingException, \
    NoDataException, \
    NoTableException, \
    BadFilterException, \
    BadRequestException, \
    LivestatusSocketException
from helper.result_manipulations import \
    make_public_service, \
    make_public_downtime, \
    make_public_host, \
    make_public_comment
from helper.filter_handling import get_filter_from_get_parameter
from lscalls.tables import get_table_entries
import json


# TODO: empty __init__.py files
# TODO: class and def documentations
# TODO: multi-downtimes
# TODO: write tests
# TODO: root resource


app = Flask(__name__)

# read and parse configuration file
config = ConfigParser.ConfigParser()
this_path = os.path.dirname(__file__) + '/'
this_path_conf = os.path.dirname(__file__) + '/conf/'
for path in ['/etc/', this_path, this_path_conf]:
    if os.path.exists(path + 'lsapi.cfg'):
        config.read(path + 'lsapi.cfg')
        app.logger.info("reading configuration file from %s" % path)
        break

c = {
    'connection_type': config.get('connection', 'type', 'AF_INET'),
    'connection_host': config.get('connection', 'host', 'localhost'),
    'connection_port': int(config.get('connection', 'port', 6557)),
    'connection_file': config.get('connection', 'socketfile', '/omd/sites/monitoring/tmp/run/live')
}

# version
version = 'v1'

# init LS accessor class
if c['connection_type'] == 'AF_INET':
    ls_socket_reader = LsSocket((c['connection_host'], c['connection_port']), c['connection_type'])
elif c['connection_type'] == 'AF_UNIX':
    ls_socket_reader = LsSocket(c['connection_file'], c['connection_type'])
else:
    raise ValueError("connection type must be either AF_INET or AF_UNIX")
    sys.exit(1)

# init LS query class

# init LS downtime class


# COMMENTS
# all comments
@app.route('/%s/comments' % version, methods=['GET'])
def g_comments():
    comment_filter = get_filter_from_get_parameter(request.args)
    return get_table_entries(ls_socket_reader, 'comments', comment_filter, False, make_public_comment)


# by id
@app.route('/%s/comment/<int:comment_id>' % version, methods=['GET'])
def get_comment(comment_id):
    filter_string = '{"eq":["id","%d"]}' % comment_id
    return get_table_entries(ls_socket_reader, 'comments', filter_string, True, make_public_comment)


# DOWNTIMES
# all downtimes (GET) and filtered (POST)
@app.route('/%s/downtimes' % version, methods=['GET', 'DELETE'])
def g_downtime():
    downtime_filter = get_filter_from_get_parameter(request.args)
    downtime_json, http_returncode = get_table_entries(ls_socket_reader, 'downtimes', downtime_filter, False, make_public_downtime, False)
    if request.method == 'GET':
        return jsonify(downtime_json), http_returncode
    elif request.method == 'DELETE':
        if downtime_filter:
            return jsonify({"message": "got a filter"})
        else:
            raise BadRequestException("no filter given, not deleting all downtimes", status_code=400)
    else:
        return jsonify({'message': 'method not allowed'}), 405

# by id. View (GET) and Delete (DELETE)
@app.route('/%s/downtime/<int:downtime_id>' % version, methods=['GET', 'DELETE'])
def get_downtime(downtime_id):
    filter_string = '{"eq":["id",%d]}' % downtime_id
    downtime_json, http_returncode = get_table_entries(ls_socket_reader, 'downtimes', filter_string, True, make_public_downtime, False)
    if request.method == 'GET':
        return jsonify(downtime_json), http_returncode
    elif request.method == 'DELETE':
        if http_returncode == 200:
            if downtime_json['downtimes']['service_display_name'] == '':
                downtime_type = 'HOST'
            else:
                downtime_type = 'SVC'
            nd = NagiosDowntime()
            delete_cmd = nd.delete_downtime(downtime_type, downtime_id)
            ls_socket_reader.connect()
            ls_socket_reader.send_command(delete_cmd)
            return jsonify({'result': 'ok'}), 200
        elif http_returncode == 404:
            return jsonify({'message': 'downtime not found'}), 404
        else:
            return jsonify({"message": "downtime lookup did not succeed"}), http_returncode
    else:
        return jsonify({'message': 'method not allowed'}), 405


# SERVICES
# get all services
@app.route('/%s/services' % version, methods=['GET'])
def get_services():
    services_filter = get_filter_from_get_parameter(request.args)
    return get_table_entries(ls_socket_reader, 'services', services_filter, False, make_public_service)

# get services by host
@app.route('/%s/services/<host>' % version, methods=['GET'])
def get_services_filtered_by_host(host):
    host_filter = '{"eq":["host_display_name", "%s"]}' % host
    return get_table_entries(ls_socket_reader, 'services', host_filter, False, make_public_service)

# get service by host and service
@app.route('/%s/service/<host>/<path:service>' % version, methods=['GET', 'POST'])
def get_service_filtered_by_host_and_service(host, service):
    unencoded_service = urllib.unquote_plus(service)
    service_filter = '{"and":[{"eq":["host_display_name","%s"]},{"eq":["service_description","%s"]}]}' \
                     % (host, unencoded_service)
    service_json = get_table_entries(ls_socket_reader, 'services', service_filter, True, make_public_service)
    if request.method == 'POST':
        downtime_datajson = request.get_json(force=True, silent=False, cache=False)
        try:
            # check if POST json contains a key 'downtime'
            downtime_data = downtime_datajson['downtime']
            downtime_identifier = 'API%06x' % random.randrange(16**6)
            if 'comment' in downtime_data.keys():
                downtime_data['comment'] = "%s: %s" % (downtime_identifier, downtime_data['comment'])
            else:
                downtime_data['comment'] = "%s: no comment provided" % downtime_identifier
        except KeyError:
            raise BadRequestException('Bad request: POST json data doesnt include a downtime key', status_code=400)
        # check if service is found in Livestatus
        j, http_returncode = service_json
        if http_returncode == 200:
            # overwrite or create service_description key in downtime_data structure
            downtime_data['service_description'] = service
            downtime_data['host_name'] = host
            # create NagiosDowntime instance
            nd = NagiosDowntime()
            # create downtime command
            downtime_cmd = nd.create_downtime('SVC', json.dumps(downtime_data))
            # send downtime command
            ls_socket_reader.connect()
            ls_socket_reader.send_command(downtime_cmd)
            # get the new created downtime via livestatus downtime table and filter 'downtime_identifier'
            downtime_filter = '{"filter":{"rei":["comment","%s"]}}' % downtime_identifier
            # allow livestatus some time to set the downtime
            for i in range(1, 5):
                time.sleep(1)
                downtime_json, http_returncode = get_table_entries(ls_socket_reader, 'downtimes', downtime_filter, True,
                                                                   make_public_downtime)
                if http_returncode == 404:
                    pass
                elif http_returncode == 200 or http_returncode == 500:
                    return downtime_json, http_returncode
                else:
                    return jsonify({"message": "unknown result from querying the new downtime"}), 500
            # result query timed out
            return jsonify({"message": "setting downtime did not succeed within 5 seconds "}), 500
        else:
            raise NoDataException("no service %s found in monitoring" % service, status_code=404)
    else:
        return service_json


# HOSTS
# get all hosts
@app.route('/%s/hosts' % version, methods=['GET'])
def get_hosts():
    hosts_filter = get_filter_from_get_parameter(request.args)
    return get_table_entries(ls_socket_reader, 'hosts', hosts_filter, False, make_public_host)


# get host by hostname
@app.route('/%s/host/<host>' % version, methods=['GET', 'POST'])
def get_host_filtered_by_name(host):
    host_filter = '{"filter":{"eq":["display_name", "%s"]}}' % host
    host_json = get_table_entries(ls_socket_reader, 'hosts', host_filter, True, make_public_host)
    if request.method == 'POST':
        downtime_datajson = request.get_json(force=True, silent=False, cache=False)
        try:
            # check if POST json contains a key 'downtime'
            downtime_data = downtime_datajson['downtime']
            downtime_identifier = 'API%06x' % random.randrange(16**6)
            if 'comment' in downtime_data.keys():
                downtime_data['comment'] = "%s: %s" % (downtime_identifier, downtime_data['comment'])
            else:
                downtime_data['comment'] = "%s: no comment provided" % downtime_identifier
        except KeyError:
            raise BadRequestException('Bad request: POST json data doesnt include a downtime key', status_code=400)
        # check if host is found in Livestatus
        j, http_returncode = host_json
        if http_returncode == 200:
            # overwrite or create host_name key in downtime_data structure
            downtime_data['host_name'] = host
            # create NagiosDowntime instance
            nd = NagiosDowntime()
            # create downtime command
            downtime_cmd = nd.create_downtime('HOST', json.dumps(downtime_data))
            # send downtime command
            ls_socket_reader.connect()
            ls_socket_reader.send_command(downtime_cmd)
            # get the new created downtime via livestatus downtime table and filter 'downtime_identifier'
            downtime_filter = '{"rei":["comment","%s"]}' % downtime_identifier
            # allow livestatus some time to set the downtime
            for i in range(1, 5):
                time.sleep(1)
                downtime_json, http_returncode = get_table_entries(ls_socket_reader, 'downtimes', downtime_filter, True,
                                                                   make_public_downtime)
                if http_returncode == 404:
                    pass
                elif http_returncode == 200 or http_returncode == 500:
                    return downtime_json, http_returncode
                else:
                    return jsonify({"message": "unknown result for querying the new downtime"}), http_returncode
            # result query timed out
            return jsonify({"error": "setting downtime did not succeed within 5 seconds "}), 500
        else:
            return NoDataException("no such host found in monitoring", status_code=404)
    else:
        # respond to GET request
        return host_json


###
# get columns and descriptions
@app.route('/%s/columns' % version, methods=['GET'])
def get_columns():
    return get_table_entries(ls_socket_reader, 'columns')

###
# stats endpoint
@app.route('/%s/stats/<entity>/<operator>/<column>/<value>' % version, methods=['GET'])
def get_stats(entity, operator, column, value):
    stats_filter = get_filter_from_get_parameter(request.args)
    stats_query = LsQuery()
    if stats_filter:
        stats_query.set_filter(json.loads(stats_filter))
    stats_query.create_stats_query(entity, column, operator, value)
    ls_socket_reader.connect()
    ls_socket_reader.send_query(stats_query)
    data = ls_socket_reader.read_query_result(stats_query)
    if data[0] == 200:
        return_data = data[1][0]
        ls_return_code = 200
    else:
        return_data = {
            'message': data[1]
        }
        ls_return_code = data[0]
    return jsonify(return_data), ls_return_code


# error handlers and helpers
@app.errorhandler(NoDataException)
@app.errorhandler(NoTableException)
@app.errorhandler(FilterParsingException)
@app.errorhandler(BadFilterException)
@app.errorhandler(BadRequestException)
@app.errorhandler(LivestatusSocketException)
def handle_api_exceptions(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"message": "resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"message": "internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)