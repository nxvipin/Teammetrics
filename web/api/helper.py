from web.models import listarchives, commitstat, commitlines
from web.lib import metrics
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
    """
    Check if a dictionary with a particular given key-value exists in a given 
    list of dictionaries.
    """
    for d in dlist:
        if d[key]==value:
            return dlist.index(d)
    return -1

def keyValueIndex(data, key, value):
    """
    Check if a dictionary with a particular given key-value exists in a given 
    list of dictionaries, if yes, returns the index of the dictionary, if no, 
    inserts and returns the index.
    """
    d = checkKeyValueExist(data, key, value)
    if d == -1 :
        kv = {}
        kv[key] = value
        data.append(kv)
        d=len(data)-1
    return d
    
def processMonthData(dbdata, metriclist):
    data = {'annualdata' : []}
    for i in dbdata:
        d = keyValueIndex(data['annualdata'],'year',int(float(i[0])))
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

def processMonthTopNData(dbdata, metriclist):
    data = {'annualdata' : []}
    for i in dbdata:
        d = keyValueIndex(data['annualdata'],'year',int(float(i[0])))
        if not data['annualdata'][d].has_key('monthlydata'):
            data['annualdata'][d]['monthlydata']=[]
        u = keyValueIndex(data['annualdata'][d]['monthlydata'],'month',int(float(i[1])))
        if not data['annualdata'][d]['monthlydata'][u].has_key('userdata'):
            data['annualdata'][d]['monthlydata'][u]['userdata']=[]
        userdata = {}
        userdata['name'] = i[2]
        userdata[metriclist[0]] = int(float(i[3]))
        try:
            userdata[metriclist[1]] = int(float(i[4]))
        except IndexError:
            pass
        data['annualdata'][d]['monthlydata'][u]['userdata'].append(userdata)
    return data

def monthList(team, mlist):
    dbdata=listarchives.monthData(mlist)
    data = processMonthData(dbdata, ['liststat'])
    data['mailing-list'] = mlist
    return data

def monthCommits(team, repo):
    dbdata=commitstat.monthData(repo)
    data=processMonthData(dbdata, ['commits'])
    data['repository'] = repo
    return data

def monthCommitLines(team, repo):
    dbdata=commitlines.monthData(repo)
    data=processMonthData( dbdata, ['lines_added', 'lines_removed'])
    data['repository'] = repo
    return data

def monthTopNList(team, mlist, n):
    dbdata=listarchives.monthTopN(mlist, n)
    data = processMonthTopNData(dbdata, ['liststat'])
    data['mailing-list'] = mlist
    return data

def monthTopNCommits(team, repo, n):
    dbdata=commitstat.monthTopN(repo, n)
    data=processMonthTopNData(dbdata, ['commits'])
    data['repository'] = repo
    return data

def monthTopNCommitLines(team, repo, n):
    dbdata=commitlines.monthTopN(repo, n)
    data=processMonthTopNData(dbdata, ['lines_added', 'lines_removed'])
    data['repository'] = repo
    return data
