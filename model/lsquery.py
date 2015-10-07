from __future__ import print_function
import StringIO
import time

from model.defaults import FILTER_CMP_OPERATORS, FILTER_BOOL_OPERATORS, KNOWN_TABLES
from api_exceptions import FilterParsingException, BadFilterException, NoTableException, LivestatusSocketException


class LsQuery:
    def __init__(self, ls_accessor):
        self.ls_accessor = ls_accessor
        self.querystring = None
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
        self.querystring = "GET %s\n%s%s%s" % (entity, columns, filter, query_postfix)
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
        self.querystring = "GET %s\nStats: %s %s %s\n%s%s" % (entity, column, operator, value, filter, query_postfix)
        self.entity = entity

    def set_filter(self, filter_dict):
        if filter_dict:
            fh = StringIO.StringIO()
            try:
                self._to_ls_filter(filter_dict, fh)
                fh.seek(0)
                self.filter = fh.read()
                fh.close()
                if self.filter == '':
                    raise FilterParsingException("error in filter parsing (parsing returned empty string)", status_code=500)
            except (RuntimeWarning, IndexError):
                raise FilterParsingException("error in filter parsing", status_code=500)
        else:
            self.filter = None

    def _to_ls_filter(self, json_dict, output):
        if isinstance(json_dict, dict):
            # loop over operations (keys)
            for operator in json_dict:
                operand = json_dict[operator]
                if operator in FILTER_CMP_OPERATORS.keys():
                    try:
                        print("Filter: %s %s %s" % (operand[0], FILTER_CMP_OPERATORS[operator], operand[1]), file=output)
                    except TypeError:
                        raise FilterParsingException("error in filter parsing", status_code=500)
                else:
                    self._to_ls_filter(operand, output)
                    if operator in FILTER_BOOL_OPERATORS.keys():
                        if operator == 'negate':
                            print("%s:" % FILTER_BOOL_OPERATORS[operator], file=output)
                        else:
                            print("%s: %s" % (FILTER_BOOL_OPERATORS[operator], len(operand)), file=output)
                    else:
                        raise BadFilterException("wrong bool filter", status_code=400)
        elif isinstance(json_dict, list):
            for l in json_dict:
                self._to_ls_filter(l, output)

    def query(self):
        """
        Query Livestatus socket
        :return: (data, livestatus_returncode)
        """
        if not self.ls_accessor:
            raise LivestatusSocketException("Livestatus Socket Error (livestatus accessor uninitialized)", status_code=500)
        self.ls_accessor.connect()
        self.ls_accessor.send(self.querystring)
        data = self.ls_accessor.read_query_result(self.fields)
        return_data = {}
        if data[0] == 200:
            return_data[self.entity] = data[1]
            ls_return_code = data[0]
        else:
            return_data['message'] = "livestatus responds '%s'" % data[1]
            ls_return_code = data[0]
        return return_data, ls_return_code

    def verify_downtimes(self, expected_entries, tries=5, interval=1):
        if not self.ls_accessor:
            raise LivestatusSocketException("Livestatus Socket Error (livestatus accessor uninitialized)", status_code=500)
        if self.entity != 'downtimes':
            raise LivestatusSocketException("LsQuery must be initialized to downtimes to verify downtimes", status_code=500)
        for t in range(0, tries):
            time.sleep(interval)
            self.ls_accessor.connect()
            self.ls_accessor.send(self.querystring)
            data = self.ls_accessor.read_query_result(self.fields)
            if data[0] == 200:
                # query succeeded. Let's count
                return_data = data[1]
                if len(return_data) == expected_entries:
                    return 200, 'found all %d newly set downtimes' % expected_entries
                else:
                    # try again
                    pass
            elif data[0] == 404:
                # not (yet) found
                pass
            else:
                return data[0], 'error looking up downtimes (%s)' % data[1]
        return 500, 'downtimes not found within %d seconds' % (tries*interval)

    def finish(self):
        self.entity = None
        self.filter = None
        self.querystring = None
        self.ls_accessor.disconnect()


class LsQueryCtx:
    def __init__(self, ls_query_instance, entity, query_filter, columns):
        self.ls_query_instance = ls_query_instance
        self.entity = entity
        self.query_filter = query_filter
        self.columns = columns

    def __enter__(self):
        self.ls_query_instance.set_filter(self.query_filter)
        self.ls_query_instance.create_table_query(self.entity, self.columns)
        return self.ls_query_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ls_query_instance.finish()
        if exc_type is not None:
            return False
        else:
            return True

