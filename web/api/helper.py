from web.models import listarchives, commitstat, commitlines, uploadstats, bugstats
from web.lib import metrics
from web.lib import metrics, log
from web import settings

logger = log.get(__name__)

def checkKeyValueExist(dlist, key, value):
    """
    Check if a dictionary with a particular given key-value exists in a given 
    list of dictionaries.
    """
    for d in dlist:
        if d.has_key(key):
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

def processData(dbdata, metriclist, n=None, datascale='month'):
    logger.info('helper.processData ')
    members = set()
    if datascale == 'month':
        if n is None:
            data = {'annualdata' : []}
            for i in dbdata:
                d = keyValueIndex(data['annualdata'],'year',i[0])
                if not data['annualdata'][d].has_key('monthlydata'):
                    data['annualdata'][d]['monthlydata']=[]
                    
                metricdata={}
                metricdata['month'] = i[1]
                metricdata[metriclist[0]] = i[2]
                try:
                    metricdata[metriclist[1]] = i[3]
                except IndexError:
                    pass
                data['annualdata'][d]['monthlydata'].append(metricdata)
            return data
        else:
            data = {'annualdata' : []}
            for i in dbdata:
                d = keyValueIndex(data['annualdata'],'year',i[0])
                if not data['annualdata'][d].has_key('monthlydata'):
                    data['annualdata'][d]['monthlydata']=[]
                u = keyValueIndex(data['annualdata'][d]['monthlydata'],'month',i[1])
                if not data['annualdata'][d]['monthlydata'][u].has_key('userdata'):
                    data['annualdata'][d]['monthlydata'][u]['userdata']=[]
                userdata = {}
                userdata['name'] = i[2]
                members.add(i[2])
                userdata[metriclist[0]] = i[3]
                try:
                    userdata[metriclist[1]] = i[4]
                except IndexError:
                    pass
                data['annualdata'][d]['monthlydata'][u]['userdata'].append(userdata)
                data['members'] = list(members)
            return data
    elif datascale == 'annual':
        if n is None:
            data = {'annualdata' : []}
            for i in dbdata:
                metricdata = {}
                metricdata['year'] = i[0]
                metricdata[metriclist[0]] = i[1]
                try:
                    metricdata[metriclist[1]] = i[2]
                except IndexError:
                    pass
                data['annualdata'].append(metricdata)
            return data
        else:
            data = {'annualdata' : []}
            for i in dbdata:
                d = keyValueIndex(data['annualdata'], 'year', i[0])
                if not data['annualdata'][d].has_key('userdata'):
                    data['annualdata'][d]['userdata'] = []
                userdata = {}
                userdata['name'] = i[1]
                members.add(i[1])
                userdata[metriclist[0]] = i[2]
                try:
                    userdata[metriclist[1]] = i[3]
                except IndexError:
                    pass
                data['annualdata'][d]['userdata'].append(userdata)
                data['members'] = list(members)
            return data

def List(team, n=None, datascale='month'):
    logger.info('List called')
    dbdata=listarchives.get(team=team, n=n, datascale=datascale)
    data = processData(dbdata, ['liststat'], n=n, datascale=datascale)
    data['mailing-list'] = team
    return data

def Commits(team, n=None, datascale='month'):
    logger.info('Commits called')
    dbdata=commitstat.get(team=team, n=n, datascale=datascale)
    data = processData(dbdata, ['commits'], n=n, datascale=datascale)
    data['repository'] = team
    return data

def Commitlines(team, n=None, datascale='month'):
    logger.info('Commitlines called')
    dbdata=commitlines.get(team=team, n=n, datascale=datascale)
    data = processData(dbdata, ['lines_added','lines_removed'], n=n, datascale=datascale)
    data['repository'] = team
    return data

def Uploadstats(team, n=None, datascale='month'):
    logger.info('Uploadstats called')
    dbdata=uploadstats.get(team=team, n=n, datascale=datascale)
    data = processData(dbdata, ['uploads'], n=n, datascale=datascale)
    data['repository'] = team
    return data

def Bugstats(team, n=None, datascale='month'):
    logger.info('Bugstats called')
    dbdata=bugstats.get(team=team, n=n, datascale=datascale)
    data = processData(dbdata, ['bugs_closed'], n=n, datascale=datascale)
    data['repository'] = team
    return data

def getData(team, metric, n=None, datascale='month'):
    logger.info('getData called')
    metricname = metrics.identify(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [List(team=m, n=n, datascale=datascale) for m in metricname]
    elif metric == 'commits':
        data['data'] = [Commits(team=m, n=n, datascale=datascale) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [Commitlines(team=m, n=n, datascale=datascale) for m in metricname]
    elif metric == 'uploads':
        data['data'] = [Uploadstats(team=m, n=n, datascale=datascale) for m in metricname]
    elif metric == 'bugs':
        data['data'] = [Bugstats(team=m, n=n, datascale=datascale) for m in metricname]
    return data

