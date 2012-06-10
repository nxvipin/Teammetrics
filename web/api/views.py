from django.http import HttpResponse
from web.models import listarchives, commitstat
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
    dbdata=listarchives.month(mlist)
    data=dict()
    data['mailing-list'] = mlist
    return _processMonthlyData(data, dbdata)

def _monthCommits(team, repo):
    dbdata=commitstat.month(repo)
    data=dict()
    data['repository'] = repo
    return _processMonthlyData(data, dbdata)

def month(request, api_version, team, metric):
    """
    Returns monthly data as JSON for a given team and metric.
    """
    logger.info("Month Function Called")
    metricname = metrics.get(team,metric)
    data = {'team' : team}
    data['data'] = {'metric' : metric}
    if metric == 'list':
        data['data']['data'] = [_monthList(team,m) for m in metricname]
    elif metric == 'repository':
        data['data']['data'] = [_monthCommits(team,m) for m in metricname]
    return HttpResponse(json.dumps(data))
