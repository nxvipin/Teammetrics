from django.http import HttpResponse
from web.models import listarchives, commitstat, commitlines
from web.lib import metrics
from web.lib import log
import json

logger = log.get(__name__)

def _checkKeyExists(dlist, key, value):
    for d in dlist:
        if d[key]==value:
            return dlist.index(d)
    return -1

def _processMonthlyData(data, dbdata):
    data['data'] = []
    for i in dbdata:
        d = _checkKeyExists(data['data'],'year',int(float(i[0])))
        if d == -1 :
            data['data'].append({'year':int(float(i[0]))})
            d=len(data['data'])-1
        if not data['data'][d].has_key('data'):
            data['data'][d]['data']=[]
        data['data'][d]['data'].append({'month':int(float(i[1])),'data':int(float(i[2]))})
    return data

def _monthList(team, mlist):
    dbdata=listarchives.monthData(mlist)
    data=dict()
    data['mailing-list'] = mlist
    return _processMonthlyData(data, dbdata)

def _monthCommits(team, repo):
    dbdata=commitstat.monthData(repo)
    data=dict()
    data['repository'] = repo
    return _processMonthlyData(data, dbdata)

def _monthCommitLines(team, repo):
    dbdata=commitlines.monthData(repo)
    data=dict()
    data['repository'] = repo
    return _processMonthlyData(data, dbdata)

def _identifyMetric(team, metric):
    if metric == 'list':
        return metrics.get(team,'list')
    elif metric == 'commits':
        return metrics.get(team,'repository')
    elif metric == 'commitlines':
        return metrics.get(team,'repository')
    else:
        return None

def month(request, api_version, team, metric):
    """
    Returns monthly data as JSON for a given team and metric.
    """
    logger.info("Month Function Called")
    metricname = _identifyMetric(team, metric)
    data = {'team' : team}
    data['data'] = {'metric' : metric}
    if metric == 'list':
        data['data']['data'] = [_monthList(team,m) for m in metricname]
    elif metric == 'commits':
        data['data']['data'] = [_monthCommits(team,m) for m in metricname]
    elif metric == 'commitlines':
        data['data']['data'] = [_monthCommitLines(team,m) for m in metricname]
        
    return HttpResponse(json.dumps(data))
