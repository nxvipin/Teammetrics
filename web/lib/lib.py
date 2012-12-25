from web import settings
from web.lib import log, metrics
import json

logger = log.get(__name__)

def jsonify(func):
    """
    JSONifies the given data and returns it.
    """
    logger.info('Jsonify Called')
    def toJson(*args, **kwargs):
        data = func(*args, **kwargs)
        return json.dumps(data)
    return toJson

def metricCheck(func):
    """
    Checks if the input metric data for input team is present in config file.
    """
    logger.info('metricCheck called')
    def check(*args, **kwargs):
        team = kwargs.get('team')
        metric = kwargs.get('metric')
        if metrics.check_metric_exist(team, metric):
            data = func(*args, **kwargs)
        else:
            data = {'error' : 'No such metric.'}
        return data
    return check

def teamCheck(func):
    """
    Checks if the data for input team is present in config file.
    """
    logger.info('teamCheck called')
    def check(*args, **kwargs):
        team = kwargs.get('team')
        if metrics.check_team_exists(team):
            data = func(*args, **kwargs)
        else:
            data = {'error' : 'No such team.'}
        return data
    return check

def versionCheck(func):
    """
    Checks if the API Version is current/supported.
    Used as a decorator over the view functions.
    """
    logger.info('versionCheck called')
    def check(*args, **kwargs):
        api_v = int(kwargs.get('api_version'))
        if api_v is settings.API_CURRENT_VERSION:
            data = func(*args, **kwargs)
            return data
        elif api_v in settings.API_SUPPORTED_VERSIONS:
            logger.info('Supported API version. ')
            data = func(*args, **kwargs)
            data['warning'] = 'A newer version of the API is available.'
            return data
        else:
            data = {'error' : 'API Version not supported'}
            logger.debug('API version not supported')
            return data
    return check

#TODO
def dateRange(request):
    """
    Returns a valid date range to passed to the SQL query by analyzing the 
    GET request.GET parameters.
    """
    startyear = request.GET.get('startyear', 'epoch')
    startmonth = request.GET.get('startmonth', '01')
    endyear = request.GET.get('endyear', 'now')
    endmonth = request.GET.get('endmonth', '12')
    startdate = 'epoch'
    enddate = 'now'
    if startyear is not 'epoch':
        if int(startyear) in range (1970,2050):
            if int(startmonth) in range(1,13):
                startdate = startyear + '-' + startmonth + '-' + '01'
    
    if endyear is not 'now':
        if int(endyear) in range (1970,2050):
            if int(endmonth) in range(1,13):
                enddate = endyear + '-' + endmonth + '-' + '01'
    
    return (startdate,enddate)
