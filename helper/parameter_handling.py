import json

from model.defaults import DEFAULT_COLUMNS, MANDATORY_COLUMNS
from helper.api_exceptions import BadFilterException, BadRequestException


def get_filter_from_get_parameter(get_args):
    # no parameter list given
    # parameter list given, but "filter" not in list
    # parameter list given including filter
    try:
        filter_arg = get_args.get('filter', None)
        if filter_arg:
            filter_dict = json.loads(filter_arg)
            if 'filter' in filter_dict:
                return_value = filter_dict['filter']
            else:
                return_value = filter_dict
        else:
            return_value = {}
    except ValueError:
        # get parameter doesn't contain filter element
        raise BadFilterException("filter parameter can't be parsed as json", status_code=400)
    return return_value


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
    if 'columns' in get_args:
        try:
            columns = json.loads(get_args.get('columns'))
            for ensurable in MANDATORY_COLUMNS[entity]:
                if ensurable not in columns:
                    columns.append(ensurable)
                return columns
        except ValueError as ve_ex:
            raise BadRequestException("cannot parse columns parameter (exception was: %s)" % str(ve_ex), status_code=400)
        except AttributeError as ae:
            raise BadRequestException("can't convert parameter columns to a list", status_code=400)
    else:
        return DEFAULT_COLUMNS[entity]

