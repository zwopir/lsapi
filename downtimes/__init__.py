from __future__ import print_function
import json
import datetime

from api_exceptions import \
    InternalProcessingException, \
    LivestatusSocketException, \
    InternalProcessingException


MANDATORY_HOST_SCHEDULE_PARAMETER = ['host_name', 'start_time', 'end_time', 'author', 'comment']
MANDATORY_SVC_SCHEDULE_PARAMETER = ['host_name', 'service_description', 'start_time', 'end_time', 'author', 'comment']
HOST_SCHEDULE_PARAMETER = ['host_name', 'start_time', 'end_time', 'fixed', 'trigger_id', 'duration', 'author', 'comment']


class NagiosDowntime:

    def __init__(self):
        self.nagios_command = None

    def create_downtime(self, downtime_type, downtime_data):
        """
        :param downtime_data: json string with parameters from nagios documentation as keys
        :return: downtime command string
        """
        if downtime_type == 'HOST':
            cmd = 'SCHEDULE_HOST_DOWNTIME'
            MANDATOR_PARAMETERS = MANDATORY_HOST_SCHEDULE_PARAMETER
        elif downtime_type == 'SVC':
            cmd = 'SCHEDULE_SVC_DOWNTIME'
            MANDATOR_PARAMETERS = MANDATORY_SVC_SCHEDULE_PARAMETER
        else:
            raise InternalProcessingException("no such downtime type. Must be 'SVC' or 'HOST'", status_code=500)

        # create dict from json
        d = json.loads(downtime_data)

        # check if all mandatory parameters are given
        mandatory_parameters_given = True
        for k in MANDATOR_PARAMETERS:
            if k not in d.keys():
                mandatory_parameters_given &= False
        if not mandatory_parameters_given:
            raise InternalProcessingException("not all mandatory parameters are given", status_code=500)

        # handle optional parameters
        if 'fixed' not in d:
            # not a fixed downtime
            d['fixed'] = 0

        if 'trigger_id' not in d:
            d['trigger_id'] = 0

        # type casting
        for k in ["start_time", "end_time"]:
            try:
                d[k] = int(d[k])
            except TypeError:
                raise InternalProcessingException("time must be specified in unix timestamp format", status_code=500)

        if 'duration' not in d:
            d['duration'] = d['end_time'] - d['start_time']
        else:
            try:
                d['duration'] = int(d['duration'])
            except TypeError:
                raise InternalProcessingException("time must be specified in unix timestamp format", status_code=500)

        # assemble command
        # now = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()
        now = timedelta_to_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1))
        if downtime_type == 'HOST':
            nagios_command = "COMMAND [%d] %s;%s;%d;%d;%d;%d;%d;%s;%s\n" \
                         % (int(now), cmd, d['host_name'], d['start_time'], d['end_time'], d['fixed'], d['trigger_id'], d['duration'], d['author'], d['comment'])
        elif downtime_type == 'SVC':
            nagios_command = "COMMAND [%d] %s;%s;%s;%d;%d;%d;%d;%d;%s;%s\n" \
                         % (int(now), cmd, d['host_name'], d['service_description'], d['start_time'], d['end_time'], d['fixed'], d['trigger_id'], d['duration'], d['author'], d['comment'])
        else:
            # already catched
            pass

        self.nagios_command = nagios_command
        return nagios_command

    def issue_downtime_command(self):
        pass

    def delete_downtime(self, downtime_type, downtime_id):
        """
        delete a downtime
        :param downtime_type: HOST or SVC
        :param downtime_id: the downtime's id
        :return: nagios command string
        """
        if downtime_type not in ['HOST', 'SVC']:
            raise LivestatusSocketException("no such downtime type, must be HOST or SVC", status_code=500)

        now = timedelta_to_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1))
        try:
            nagios_command = "COMMAND [%d] DEL_%s_DOWNTIME;%d\n" % (now, downtime_type, int(downtime_id))
        except TypeError:
            InternalProcessingException("downtime id must be an integer", status_code=500)
        return nagios_command


def timedelta_to_seconds(td):
    """
    convert a timedelta object to seconds
    :param td:
    :return: timedelta in seconds, rounded to int
    """
    # python 2.7 has total_seconds, but in case we're using python 2.6...
    return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

