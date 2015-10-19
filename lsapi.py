#!/usr/bin/env python
from __future__ import print_function
import urllib
from flask import Flask, request, jsonify
from model.lsquery import LsQuery, LsQueryCtx
from model.socket_communication import LsSocket
from api_exceptions import \
    FilterParsingException, \
    NoDataException, \
    NoTableException, \
    BadFilterException, \
    BadRequestException, \
    LivestatusSocketException, \
    InternalProcessingException
from helper.filter_handling import \
    get_filter_from_get_parameter, \
    get_columns_from_get_parameter_or_use_defaults, \
    filter_to_dict
from controller.actions import LivestatusActionCtx
from configuration.socket_config import SocketConfiguration


# TODO: class and def documentations
# TODO: write tests

app = Flask(__name__)

# version
version = 'v1'


config = SocketConfiguration(__file__)

ls_accessor = LsSocket(config.connection_string, config.connection_type)
# init LS query class
ls_query = LsQuery(ls_accessor)

@app.route('/%s/columns' % version, methods=['GET'])
def get_columns():
    entity = 'columns'
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    query_filter = get_filter_from_get_parameter(request.args)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            return task_ctx.return_table()


# COMMENTS
# all comments
@app.route('/%s/comments' % version, methods=['GET'])
def g_comments():
    entity = 'comments'
    query_filter = get_filter_from_get_parameter(request.args)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            return task_ctx.return_table()


# by id
@app.route('/%s/comments/<int:comment_id>' % version, methods=['GET'])
def get_comment(comment_id):
    entity = 'comments'
    query_filter = filter_to_dict('{"eq":["id","%d"]}' % comment_id)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            return task_ctx.return_table()


# DOWNTIMES
# get all downtimes (GET)
# delete downtimes specified by filter (DELETE)
@app.route('/%s/downtimes' % version, methods=['GET', 'DELETE'])
def g_downtime():
    entity = 'downtimes'
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    query_filter = get_filter_from_get_parameter(request.args)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'GET':
                return task_ctx.return_table()
            elif request.method == 'DELETE':
                if query_filter:
                    return task_ctx.delete_downtime(ls_ctx)
                else:
                    raise BadRequestException("no filter given, not deleting all downtimes", status_code=400)


# by id. View (GET) and Delete (DELETE)
@app.route('/%s/downtimes/<int:downtime_id>' % version, methods=['GET', 'DELETE'])
def get_downtime(downtime_id):
    entity = 'downtimes'
    query_filter = filter_to_dict('{"eq":["id",%d]}' % downtime_id)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'GET':
                return task_ctx.return_table()
            elif request.method == 'DELETE':
                return task_ctx.delete_downtime(ls_ctx)



# SERVICES
# get all services
@app.route('/%s/services' % version, methods=['GET', 'POST'])
def get_services():
    entity = 'services'
    query_filter = get_filter_from_get_parameter(request.args)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'POST':
                if not query_filter:
                    raise BadRequestException("no filter given, not setting downtime on all services", status_code=400)
                downtime_data = request.get_json(force=True, silent=False, cache=False)
                count, downtime_identifier = task_ctx.set_downtime(ls_ctx, downtime_data)
                # verify new downtimes
                downtime_filter = filter_to_dict('{"rei": ["comment", "%s"]}' % downtime_identifier)
                downtime_columns = get_columns_from_get_parameter_or_use_defaults({}, 'downtimes')
                with LsQueryCtx(ls_query, 'downtimes', downtime_filter, downtime_columns) as downtime_ls_ctx:
                    downtime_return_code, message = downtime_ls_ctx.verify_downtimes(count)
                    return jsonify({"message": message}), downtime_return_code
            else:
                # GET request
                return task_ctx.return_table()



# get services by host
@app.route('/%s/services/<host>' % version, methods=['GET', 'POST'])
def get_services_filtered_by_host(host):
    entity = 'services'
    query_filter = filter_to_dict('{"eq":["host_display_name", "%s"]}' % host)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'POST':
                downtime_data = request.get_json(force=True, silent=False, cache=False)
                count, downtime_identifier = task_ctx.set_downtime(ls_ctx, downtime_data)
                # verify new downtimes
                downtime_filter = filter_to_dict('{"rei": ["comment", "%s"]}' % downtime_identifier)
                downtime_columns = get_columns_from_get_parameter_or_use_defaults({}, 'downtimes')
                with LsQueryCtx(ls_query, 'downtimes', downtime_filter, downtime_columns) as downtime_ls_ctx:
                    downtime_return_code, message = downtime_ls_ctx.verify_downtimes(count)
                    return jsonify({"message": message}), downtime_return_code
            else:
                return task_ctx.return_table()


# get service by host and service
@app.route('/%s/services/<host>/<path:service>' % version, methods=['GET', 'POST'])
def get_service_filtered_by_host_and_service(host, service):
    entity = 'services'
    unencoded_service = urllib.unquote_plus(service)
    query_filter = filter_to_dict('{"and":[{"eq":["host_display_name","%s"]},{"eq":["service_description","%s"]}]}'
                                  % (host, unencoded_service))
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'POST':
                downtime_data = request.get_json(force=True, silent=False, cache=False)
                count, downtime_identifier = task_ctx.set_downtime(ls_ctx, downtime_data)
                # verify new downtimes
                downtime_filter = filter_to_dict('{"rei": ["comment", "%s"]}' % downtime_identifier)
                downtime_columns = get_columns_from_get_parameter_or_use_defaults({}, 'downtimes')
                with LsQueryCtx(ls_query, 'downtimes', downtime_filter, downtime_columns) as downtime_ls_ctx:
                    downtime_return_code, message = downtime_ls_ctx.verify_downtimes(count)
                    return jsonify({"message": message}), downtime_return_code
            else:
                return task_ctx.return_table()


# HOSTS
# get all hosts
@app.route('/%s/hosts' % version, methods=['GET', 'POST'])
def get_hosts():
    entity = 'hosts'
    query_filter = get_filter_from_get_parameter(request.args)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'POST':
                if not query_filter:
                    raise BadRequestException("no filter given, not setting downtime on all hosts", status_code=400)
                downtime_data = request.get_json(force=True, silent=False, cache=False)
                count, downtime_identifier = task_ctx.set_downtime(ls_ctx, downtime_data)
                # verify new downtimes
                downtime_filter = filter_to_dict('{"rei": ["comment", "%s"]}' % downtime_identifier)
                downtime_columns = get_columns_from_get_parameter_or_use_defaults({}, 'downtimes')
                with LsQueryCtx(ls_query, 'downtimes', downtime_filter, downtime_columns) as downtime_ls_ctx:
                    downtime_return_code, message = downtime_ls_ctx.verify_downtimes(count)
                    return jsonify({"message": message}), downtime_return_code
            else:
                # GET request
                return task_ctx.return_table()

# get host by hostname
@app.route('/%s/hosts/<host>' % version, methods=['GET', 'POST'])
def get_host_filtered_by_name(host):
    entity = 'hosts'
    query_filter = filter_to_dict('{"eq":["display_name", "%s"]}' % host)
    columns = get_columns_from_get_parameter_or_use_defaults(request.args, entity)
    with LsQueryCtx(ls_query, entity, query_filter, columns) as ls_ctx:
        data, ls_return_code = ls_ctx.query()
        with LivestatusActionCtx(data, ls_return_code) as task_ctx:
            if request.method == 'POST':
                downtime_data = request.get_json(force=True, silent=False, cache=False)
                count, downtime_identifier = task_ctx.set_downtime(ls_ctx, downtime_data)
                # verify new downtimes
                downtime_filter = filter_to_dict('{"rei": ["comment", "%s"]}' % downtime_identifier)
                downtime_columns = get_columns_from_get_parameter_or_use_defaults({}, 'downtimes')
                with LsQueryCtx(ls_query, 'downtimes', downtime_filter, downtime_columns) as downtime_ls_ctx:
                    downtime_return_code, message = downtime_ls_ctx.verify_downtimes(count)
                    return jsonify({"message": message}), downtime_return_code
            else:
                # GET request
                return task_ctx.return_table()


###
# stats endpoint
@app.route('/%s/stats/<entity>/<operator>/<column>/<value>' % version, methods=['GET'])
def get_stats(entity, operator, column, value):
    stats_filter = get_filter_from_get_parameter(request.args)
    ls_query.set_filter(stats_filter)
    ls_query.create_stats_query(entity, column, operator, value)
    data, ls_return_code = ls_query.query()
    return jsonify(data[entity][0]), ls_return_code


# error handlers and helpers
@app.errorhandler(NoDataException)
@app.errorhandler(NoTableException)
@app.errorhandler(FilterParsingException)
@app.errorhandler(BadFilterException)
@app.errorhandler(BadRequestException)
@app.errorhandler(LivestatusSocketException)
@app.errorhandler(InternalProcessingException)
def handle_api_exceptions(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(400)
def bad_request(_):
    return jsonify({"message": "bad request"}), 400


@app.errorhandler(404)
def page_not_found(_):
    return jsonify({"message": "resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"message": "method not allowed"}), 405


@app.errorhandler(500)
def internal_server_error(_):
    return jsonify({"message": "internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)