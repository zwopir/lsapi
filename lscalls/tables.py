import json
from flask import jsonify
from api_exceptions import NoTableException
from data.defaults import KNOWN_TABLES, DEFAULT_COLUMNS
from lsquery import LsQuery
from helper.result_manipulations import \
    identity, \
    make_public_downtime, \
    make_public_comment, \
    make_public_host, \
    make_public_service, \
    comments2array, \
    downtimes2array, \
    cast_fields


def get_table_entries(ls_socket_reader,
                      lstable,
                      filter='',
                      first=False,
                      make_public_function=identity,
                      return_jsonified=True):
    if lstable in KNOWN_TABLES:
        entity = lstable
    else:
        raise NoTableException("table %s doesn't exist" % lstable, status_code=404)
    # handle filter parameter
    get_query = LsQuery()
    if filter:
        filter_dict = json.loads(filter)
        if 'filter' in filter_dict:
            get_query.set_filter(filter_dict['filter'])
        else:
            get_query.set_filter(filter_dict)
    get_query.create_table_query(entity, DEFAULT_COLUMNS[entity])
    ls_socket_reader.connect()
    ls_socket_reader.send_query(get_query)
    data = ls_socket_reader.read_query_result(get_query)
    return_data = {}
    if data[0] == 200:
        public_data = [cast_fields(element) for element in data[1]]
        public_data = [make_public_function(element) for element in public_data]
        public_data = [downtimes2array(element) for element in public_data]
        public_data = [comments2array(element) for element in public_data]
        if first:
            return_data[entity] = public_data[0]
            ls_return_code = data[0]
        else:
            return_data[entity] = public_data
            ls_return_code = data[0]
    else:
        return_data['message'] = data[1]
        ls_return_code = data[0]
    if return_jsonified:
        return jsonify(return_data), ls_return_code
    else:
        return return_data, ls_return_code