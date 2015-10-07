import datetime

from api_exceptions import \
    LivestatusSocketException, \
    InternalProcessingException


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


class NagiosCommand:

    def __init__(self, ls_accessor):
        self.nagios_command = None
        self.ls_accessor = ls_accessor

    def create_downtime(self, downtime_type, downtime_dict):
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
            raise InternalProcessingException("not all mandatory downtime parameters are given", status_code=500)

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
                raise InternalProcessingException("time must be specified in unix timestamp format", status_code=500)

        if 'duration' not in downtime_dict:
            downtime_dict['duration'] = downtime_dict['end_time'] - downtime_dict['start_time']
        else:
            try:
                downtime_dict['duration'] = int(downtime_dict['duration'])
            except TypeError:
                raise InternalProcessingException("time must be specified in unix timestamp format", status_code=500)

        # assemble command
        now = timedelta_to_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1))
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

        # self.nagios_command = nagios_command
        self.ls_accessor.connect()
        self.ls_accessor.send(nagios_command)
        return nagios_command

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
        self.ls_accessor.connect()
        self.ls_accessor.send(nagios_command)
        return nagios_command


def timedelta_to_seconds(td):
    """
    convert a timedelta object to seconds
    :param td:
    :return: timedelta in seconds, rounded to int
    """
    # python 2.7 has total_seconds, but in case we're using python 2.6...
    return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

