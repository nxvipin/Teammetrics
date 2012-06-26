from web.models import listarchives, commitstat, commitlines
from web.lib import metrics
from web.lib import metrics, log
from web.api import settings

logger = log.get(__name__)

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

def processAnnualData(dbdata, metriclist):
    data = {'annualdata' : []}
    for i in dbdata:
        metricdata = {}
        metricdata['year'] = int(float(i[0]))
        metricdata[metriclist[0]] = int(float(i[1]))
        try:
            metricdata[metriclist[1]] = int(float(i[2]))
        except IndexError:
            pass
        data['annualdata'].append(metricdata)
    return data

def processAnnualTopNData(dbdata, metriclist):
    data = {'annualdata' : []}
    for i in dbdata:
        d = keyValueIndex(data['annualdata'], 'year', int(float(i[0])))
        if not data['annualdata'][d].has_key('userdata'):
            data['annualdata'][d]['userdata'] = []
        userdata = {}
        userdata['name'] = i[1]
        userdata[metriclist[0]] = int(float(i[2]))
        try:
            userdata[metriclist[1]] = int(float(i[3]))
        except IndexError:
            pass
        data['annualdata'][d]['userdata'].append(userdata)
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

def annualList(team, mlist):
    dbdata=listarchives.annualData(mlist)
    data = processAnnualData(dbdata, ['liststat'])
    data['mailing-list'] = mlist
    return data

def annualCommits(team, repo):
    dbdata=commitstat.annualData(repo)
    data=processAnnualData(dbdata, ['commits'])
    data['repository'] = repo
    return data

def annualCommitLines(team, repo):
    dbdata=commitlines.annualData(repo)
    data=processAnnualData( dbdata, ['lines_added', 'lines_removed'])
    data['repository'] = repo
    return data

def annualTopNList(team, mlist, n):
    dbdata=listarchives.annualTopN(mlist, n)
    data = processAnnualTopNData(dbdata, ['liststat'])
    data['mailing-list'] = mlist
    return data

def annualTopNCommits(team, repo, n):
    dbdata=commitstat.annualTopN(repo, n)
    data=processAnnualTopNData(dbdata, ['commits'])
    data['repository'] = repo
    return data

def annualTopNCommitLines(team, repo, n):
    dbdata=commitlines.annualTopN(repo, n)
    data=processAnnualTopNData(dbdata, ['lines_added', 'lines_removed'])
    data['repository'] = repo
    return data

def getMonthData(api_version, team, metric):
    """
    Returns JSON ready monthly data for a given team and metric.
    """
    metricname = identifyMetric(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [monthList(team,m) for m in metricname]
    elif metric == 'commits':
        data['data'] = [monthCommits(team,m) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [monthCommitLines(team,m) for m in metricname]
    return data

def getMonthTopNData(api_version, team, metric, n):
    """
    Returns JSON ready monthly top N data for a given team and metric.
    """
    metricname = identifyMetric(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [monthTopNList(team,m,n) for m in metricname]
    elif metric == 'commits':
        data['data'] = [monthTopNCommits(team,m,n) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [monthTopNCommitLines(team,m,n) for m in metricname]
    return data

def getAnnualData(api_version, team, metric):
    """
    Returns JSON ready monthly data for a given team and metric.
    """
    metricname = identifyMetric(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [annualList(team,m) for m in metricname]
    elif metric == 'commits':
        data['data'] = [annualCommits(team,m) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [annualCommitLines(team,m) for m in metricname]
    return data

def getAnnualTopNData(api_version, team, metric, n):
    """
    Returns JSON ready monthly top N data for a given team and metric.
    """
    metricname = identifyMetric(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [annualTopNList(team,m,n) for m in metricname]
    elif metric == 'commits':
        data['data'] = [annualTopNCommits(team,m,n) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [annualTopNCommitLines(team,m,n) for m in metricname]
    return data
