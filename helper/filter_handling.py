import json

def get_filter_from_get_parameter(get_args):
    # no parameter list given
    # parameter list given, but "filter" not in list
    # parameter list given including filter
    try:
        filter_string = get_args.get('filter', None)
    except KeyError:
        # get parameter doesn't contain filter element
        raise BadFilterException("get parameter doesn't contain a filter element", status_code=400)
    return filter_string


def filter_to_dict(filter_string):
    filter_dict = json.loads(filter_string)
    if 'filter' in filter_dict:
        return filter_dict['filter']
    else:
        return filter_dict


