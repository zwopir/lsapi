import json

from model.defaults import DEFAULT_COLUMNS, MANDATORY_COLUMNS
from api_exceptions import BadFilterException, BadRequestException


def get_filter_from_get_parameter(get_args):
    # no parameter list given
    # parameter list given, but "filter" not in list
    # parameter list given including filter
    try:
        filter = get_args.get('filter', None)
        if filter:
            filter_dict = json.loads(filter)
            if 'filter' in filter_dict:
                retval = filter_dict['filter']
            else:
                retval = filter_dict
        else:
            retval = {}
    except ValueError:
        # get parameter doesn't contain filter element
        raise BadFilterException("filter parameter can't be parsed as json", status_code=400)
    return retval


def filter_to_dict(filter_string):
    try:
        filter_dict = json.loads(filter_string)
        if 'filter' in filter_dict:
            return filter_dict['filter']
        else:
            return filter_dict
    except ValueError:
        raise BadFilterException("filter parameter can't be parsed as json", status_code=400)


def get_columns_from_get_parameter_or_use_defaults(get_args, entity):
    if get_args.has_key('columns'):
        try:
            columns = json.loads(get_args.get('columns'))
            for ensurable in MANDATORY_COLUMNS[entity]:
                if ensurable not in columns:
                    columns.append(ensurable)
            if isinstance(columns, list):
                return columns
            else:
                raise BadRequestException("can't convert parameter columns to a list. Must be a json array")
        except ValueError as ve_ex:
            raise BadRequestException("cannot parse columns parameter (exception was: %s)" % str(ve_ex), status_code=400)
    else:
        return DEFAULT_COLUMNS[entity]

