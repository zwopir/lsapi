__author__ = 'oelmuellerc'

DEFAULT_COLUMNS = {
    "hosts": [
        "acknowledged",
        "address",
        "comments",
        "name",
        "display_name",
        "downtimes",
        "last_state",
        "last_hard_state"
    ],
    "services": [
        "acknowledged",
        "comments",
        "description",
        "display_name",
        "downtimes",
        "host_display_name",
        "host_downtimes",
        "host_scheduled_downtime_depth",
        "last_state",
        "last_hard_state",
        "scheduled_downtime_depth"
    ],
    "downtimes": [
        "id",
        "author",
        "comment",
        "duration",
        "start_time",
        "end_time",
        "entry_time",
        "fixed",
        "host_display_name",
        "service_display_name",
        "is_service"
    ],
    "columns": [
        "table",
        "name",
        "description",
        "type"
    ],
    "comments": [
        "id",
        "author",
        "comment",
        "entry_time",
        "entry_type",
        "expire_time",
        "expires",
        "host_display_name",
        "service_display_name"
    ],
}

KNOWN_TABLES = [key for key in DEFAULT_COLUMNS]
MANDATORY_COLUMNS = {
    "hosts": [
        "display_name",
        "is_service"
    ],
    "services": [
        "host_display_name",
        "display_name",
        "is_service"
    ],
    "downtimes": [
        "id",
        "is_service"
    ],
    "columns": [
    ],
    "comments": [
        "id",
    ],
}

INTEGER_COLUMNS = [
    "last_state",
    "last_hard_state",
    "scheduled_downtime_depth",
    "host_scheduled_downtime_depth",
    "id",
    "duration",
    "start_time",
    "end_time",
    "entry_time",
    "fixed",
    "expire_time",
    "acknowledged",
    "entry_type",
    "expires",
    "is_service"
]

FILTER_CMP_OPERATORS = {
    'eq': '=',
    're': '~',
    'eqi': '=~',
    'rei': '~~',
    'lt': '<',
    'gt': '>',
    'le': '<=',
    'ge': '>=',
    'neq': '!=',
    'nre': '!~',
    'neqi': '!=~',
    'nrei': '!~~',
}

FILTER_BOOL_OPERATORS = {
    'and': 'And',
    'or': 'Or',
    'negate': 'Negate'
}


