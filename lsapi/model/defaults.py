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
        "service_state",
        "host_state",
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
    ],
    "services": [
        "host_display_name",
        "display_name",
    ],
    "downtimes": [
        "id",
        "is_service"
    ],
    "columns": [
        "name"
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
    "is_service",
    "service_state",
    "host_state"
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

MANDATORY_HOST_SCHEDULE_PARAMETER = [
    'host_name',
    'start_time',
    'end_time',
    'author',
    'comment'
]
MANDATORY_SVC_SCHEDULE_PARAMETER = [
    'host_name',
    'service_description',
    'start_time',
    'end_time',
    'author',
    'comment'
]
HOST_SCHEDULE_PARAMETER = [
    'host_name',
    'start_time',
    'end_time',
    'fixed',
    'trigger_id',
    'duration',
    'author',
    'comment'
]


