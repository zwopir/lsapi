__author__ = 'oelmuellerc'

DEFAULT_COLUMNS = {}
DEFAULT_COLUMNS["hosts"] = ["acknowledged", "address", "comments", "name", "display_name", "downtimes", "last_state", "last_hard_state"]
DEFAULT_COLUMNS["services"] = ["acknowledged", "comments", "description", "display_name", "downtimes", "host_display_name", "host_downtimes", "host_scheduled_downtime_depth", "last_state", "last_hard_state", "scheduled_downtime_depth"]
DEFAULT_COLUMNS["downtimes"] = ["id", "author", "comment", "duration", "start_time", "end_time", "entry_time", "fixed", "host_display_name", "service_display_name"]
DEFAULT_COLUMNS["columns"] = ["table", "name", "description", "type"]
DEFAULT_COLUMNS["comments"] = ["id", "author", "comment", "entry_time", "entry_type", "expire_time", "expires", "host_display_name", "service_display_name"]
KNOWN_TABLES = [key for key in DEFAULT_COLUMNS]

INTEGER_COLUMNS = [
    "last_state",
    "last_hard_state",
    "scheduled_downtime_depth",
    "id",
    "duration",
    "start_time",
    "end_time",
    "entry_time",
    "fixed",
    "expire_time",
    "acknowledged"
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

