from django.http import HttpResponse
from web.models import listarchives, commitstat, commitlines
from web.lib import metrics
from web.lib import log
from web.api import helper
import json

logger = log.get(__name__)

def _monthList(team, mlist):
    dbdata=listarchives.monthData(mlist)
    data=dict()
    data['mailing-list'] = mlist
    return helper.processMonthlyData(data, dbdata, ['liststat'])

def _monthCommits(team, repo):
    dbdata=commitstat.monthData(repo)
    data=dict()
    data['repository'] = repo
    return helper.processMonthlyData(data, dbdata, ['commits'])

def _monthCommitLines(team, repo):
    dbdata=commitlines.monthData(repo)
    data=dict()
    data['repository'] = repo
    return helper.processMonthlyData(data, dbdata, ['lines_added', 'lines_removed'])

def month(request, api_version, team, metric):
    """
    Returns monthly data as JSON for a given team and metric.
    """
    logger.info("Month Function Called")
    metricname = helper.identifyMetric(team, metric)
    data = {'team' : team}
    data['data'] = {'metric' : metric}
    if metric == 'list':
        data['data']['data'] = [_monthList(team,m) for m in metricname]
    elif metric == 'commits':
        data['data']['data'] = [_monthCommits(team,m) for m in metricname]
    elif metric == 'commitlines':
        data['data']['data'] = [_monthCommitLines(team,m) for m in metricname]
        
    return HttpResponse(json.dumps(data))
