from web.lib import metrics, log
from web.api import settings

logger = log.get(__name__)

def identifyMetric(team, metric):
    """
    Identifies the metric specified in the API using the data in config file.
    Return a list containing the metric name(s) for the team.
    """
    if metric == 'list':
        return metrics.get(team,'list')
    elif metric == 'commits':
        return metrics.get(team,'repository')
    elif metric == 'commitlines':
        return metrics.get(team,'repository')
    else:
        logger.info('Incorrect Metric Identifier')
        return []

def version(api_version):
    if api_version in settings.API_SUPPORTED_VERSIONS:
        return True
    else:
        return False

def checkKeyValueExist(dlist, key, value):
    for d in dlist:
        if d[key]==value:
            return dlist.index(d)
    return -1

def processMonthlyData(data, dbdata, metriclist):
    data['annualdata'] = []
    for i in dbdata:
        d = checkKeyValueExist(data['annualdata'],'year',int(float(i[0])))
        if d == -1 :
            data['annualdata'].append({'year':int(float(i[0]))})
            d=len(data['annualdata'])-1
        if not data['annualdata'][d].has_key('monthlydata'):
            data['annualdata'][d]['monthlydata']=[]
            
        metricdata={}
        metricdata['month'] = int(float(i[1]))
        metricdata[metriclist[0]] = int(float(i[2]))
        try:
            metricdata[metriclist[1]] = int(float(i[3]))
        except IndexError:
            pass
        data['annualdata'][d]['monthlydata'].append(metricdata)
    return data
