from __future__ import print_function
import StringIO
import time
import datetime
from defaults import FILTER_CMP_OPERATORS, \
    FILTER_BOOL_OPERATORS, \
    KNOWN_TABLES, \
    MANDATORY_HOST_SCHEDULE_PARAMETER, \
    MANDATORY_SVC_SCHEDULE_PARAMETER
from lsapi.helper.api_exceptions import FilterParsingException, \
    BadFilterException, \
    BadRequestException, \
    NoTableException, \
    LivestatusSocketException, \
    InternalProcessingException


class Query:
    def __init__(self, ls_accessor):
        self.ls_accessor = ls_accessor
        self.querystring = None
        self.fields = None
        self.entity = None
        self.filter = None
        self.send_only = False

    def __str__(self):
        return "LsQuery for %s" % self.entity

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
        self.ls_accessor.send(self)
        if not self.send_only:
            data = self.ls_accessor.read_query_result(self)
            return_data = {}
            if data[0] == 200:
                return_data[self.entity] = data[1]
                ls_return_code = data[0]
            else:
                return_data['message'] = "livestatus responds '%s'" % data[1]
                ls_return_code = data[0]
            return return_data, ls_return_code
        else:
            return {"message": "send nagios command"}, 200

    def verify_downtimes(self, expected_entries, tries=5, interval=1):
        if not self.ls_accessor:
            raise LivestatusSocketException("Livestatus Socket Error (livestatus accessor uninitialized)", status_code=500)
        if self.entity != 'downtimes':
            raise LivestatusSocketException("LsQuery must be initialized to downtimes to verify downtimes", status_code=500)
        for t in range(0, tries):
            time.sleep(interval)
            self.ls_accessor.connect()
            self.ls_accessor.send(self)
            # TODO: don't read in as list, but as (returncode, data)
            data = self.ls_accessor.read_query_result(self)
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
        self.send_only = False

    def create_downtime_query(self, downtime_type, downtime_dict):
        self.send_only = True
        if downtime_type == 'HOST':
            cmd = 'SCHEDULE_HOST_DOWNTIME'
            MANDATOR_PARAMETERS = MANDATORY_HOST_SCHEDULE_PARAMETER
        elif downtime_type == 'SVC':
            cmd = 'SCHEDULE_SVC_DOWNTIME'
            MANDATOR_PARAMETERS = MANDATORY_SVC_SCHEDULE_PARAMETER
        else:
            raise InternalProcessingException("no such downtime type. Must be 'SVC' or 'HOST'", status_code=500)

        # check if all mandatory parameters are given
        mandatory_parameters_given = True
        for k in MANDATOR_PARAMETERS:
            if k not in downtime_dict.keys():
                mandatory_parameters_given &= False
        if not mandatory_parameters_given:
            raise BadRequestException("not all mandatory downtime parameters are given", status_code=400)

        # handle optional parameters
        if 'fixed' not in downtime_dict:
            # not a fixed downtime
            downtime_dict['fixed'] = 0

        if 'trigger_id' not in downtime_dict:
            downtime_dict['trigger_id'] = 0

        # type casting
        for k in ["start_time", "end_time"]:
            try:
                downtime_dict[k] = int(downtime_dict[k])
            except TypeError:
                raise BadRequestException("time must be specified in unix timestamp format", status_code=400)

        if 'duration' not in downtime_dict:
            downtime_dict['duration'] = downtime_dict['end_time'] - downtime_dict['start_time']
        else:
            try:
                downtime_dict['duration'] = int(downtime_dict['duration'])
            except TypeError:
                raise BadRequestException("time must be specified in unix timestamp format", status_code=400)

        # assemble command
        now = self._timedelta_to_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1))
        if downtime_type == 'HOST':
            nagios_command = "COMMAND [%d] %s;%s;%d;%d;%d;%d;%d;%s;%s\n" % (
                int(now),
                cmd,
                downtime_dict['host_name'],
                downtime_dict['start_time'],
                downtime_dict['end_time'],
                downtime_dict['fixed'],
                downtime_dict['trigger_id'],
                downtime_dict['duration'],
                downtime_dict['author'],
                downtime_dict['comment'])
        else:
            # downtime_type == 'SVC':
            nagios_command = "COMMAND [%d] %s;%s;%s;%d;%d;%d;%d;%d;%s;%s\n" % (
                int(now),
                cmd,
                downtime_dict['host_name'],
                downtime_dict['service_description'],
                downtime_dict['start_time'],
                downtime_dict['end_time'],
                downtime_dict['fixed'],
                downtime_dict['trigger_id'],
                downtime_dict['duration'],
                downtime_dict['author'],
                downtime_dict['comment'])

        self.querystring = nagios_command
        return nagios_command

    def delete_downtime_query(self, downtime_type, downtime_id):
        """
        delete a downtime
        :param downtime_type: HOST or SVC
        :param downtime_id: the downtime's id
        :return: nagios command string
        """
        self.send_only = True
        if downtime_type not in ['HOST', 'SVC']:
            raise LivestatusSocketException("no such downtime type, must be HOST or SVC", status_code=500)

        now = self._timedelta_to_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1))
        try:
            nagios_command = "COMMAND [%d] DEL_%s_DOWNTIME;%d\n" % (now, downtime_type, int(downtime_id))
        except TypeError:
            InternalProcessingException("downtime id must be an integer", status_code=500)
        self.querystring = nagios_command
        return nagios_command

    def _timedelta_to_seconds(self, td):
        """
        convert a timedelta object to seconds
        :param td:
        :return: timedelta in seconds, rounded to int
        """
        # python 2.7 has total_seconds, but in case we're using python 2.6...
        return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)


class QueryTableCtx:
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


class QueryStatsCtx:
    def __init__(self, ls_query_instance, entity, query_filter, column, operator, value):
        self.ls_query_instance = ls_query_instance
        self.entity = entity
        self.query_filter = query_filter
        self.column = column
        self.operator = operator
        self.value = value

    def __enter__(self):
        self.ls_query_instance.set_filter(self.query_filter)
        self.ls_query_instance.create_stats_query(self.entity,
                                                  self.column,
                                                  self.operator,
                                                  self.value)
        return self.ls_query_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ls_query_instance.finish()
        if exc_type is not None:
            return False
        else:
            return True
