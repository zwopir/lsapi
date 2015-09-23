from __future__ import print_function
import StringIO
from data.defaults import FILTER_CMP_OPERATORS, FILTER_BOOL_OPERATORS, KNOWN_TABLES
from api_exceptions import FilterParsingException, BadFilterException, NoTableException


class LsQuery:
    def __init__(self):
        self.query = None
        self.fields = None
        self.entity = None
        self.filter = None

    def create_table_query(self, entity, fields, query_postfix="OutputFormat: csv\nResponseHeader: fixed16\n"):
        if entity not in KNOWN_TABLES:
            raise NoTableException("no such table %s" % entity, status_code=500)
        columns = "Columns: " + ' '.join(fields) + "\n"
        if self.filter is None:
            filter = ''
        else:
            filter = self.filter
        self.query = "GET %s\n%s%s%s" % (entity, columns, filter, query_postfix)
        self.fields = fields
        self.entity = entity

    def create_stats_query(self, entity, column, operator, value, query_postfix="OutputFormat: csv\nResponseHeader: fixed16\n"):
        if entity not in KNOWN_TABLES:
            raise NoTableException("no such table %s" % entity, status_code=400)
        if self.filter is None:
            filter = ''
        else:
            filter = self.filter
        try:
            operator = FILTER_CMP_OPERATORS[operator]
        except KeyError:
            raise BadFilterException("unknown compare operator %s" % operator)
        self.fields = ["count"]
        self.query = "GET %s\nStats: %s %s %s\n%s%s" % (entity, column, operator, value, filter, query_postfix)
        self.entity = entity

    def set_filter(self, filter_dict):
        if filter_dict:
            fh = StringIO.StringIO()
            try:
                self.to_ls_filter(filter_dict, fh)
                fh.seek(0)
                self.filter = fh.read()
                fh.close()
                if self.filter == '':
                    raise FilterParsingException("error in filter parsing (parsing returned empty string)", status_code=500)
            except (RuntimeWarning, IndexError):
                raise FilterParsingException("error in filter parsing", status_code=500)

    def to_ls_filter(self, json_dict, output):
        if isinstance(json_dict, dict):
            # loop over operations (keys)
            for operator in json_dict:
                operand = json_dict[operator]
                if operator in FILTER_CMP_OPERATORS.keys():
                    try:
                        print("Filter: %s %s %s" % (operand[0], FILTER_CMP_OPERATORS[operator], operand[1]), file=output)
                    except TypeError:
                        raise FilterParsingException("3 error in filter parsing", status_code=500)
                else:
                    self.to_ls_filter(operand, output)
                    if operator in FILTER_BOOL_OPERATORS.keys():
                        if operator == 'negate':
                            print("%s:" % FILTER_BOOL_OPERATORS[operator], file=output)
                        else:
                            print("%s: %s" % (FILTER_BOOL_OPERATORS[operator], len(operand)), file=output)
                    else:
                        raise BadFilterException("wrong bool filter", status_code=400)
        elif isinstance(json_dict, list):
            for l in json_dict:
                self.to_ls_filter(l, output)