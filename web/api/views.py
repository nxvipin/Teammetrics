from django.http import HttpResponse
from web.lib import log
from web.api import helper
import json

logger = log.get(__name__)

def getMonthData(api_version, team, metric):
    """
    Returns JSON ready monthly data for a given team and metric.
    """
    logger.info("Month Function Called")
    metricname = helper.identifyMetric(team, metric)
    data = {'metric' : metric}
    if metric == 'list':
        data['data'] = [helper.monthList(team,m) for m in metricname]
    elif metric == 'commits':
        data['data'] = [helper.monthCommits(team,m) for m in metricname]
    elif metric == 'commitlines':
        data['data'] = [helper.monthCommitLines(team,m) for m in metricname]
    return data

def month(request, api_version, team, metric):
    data = getMonthData(api_version, team, metric)
    data['team'] = team
    return HttpResponse(json.dumps(data))

def monthAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(getMonthData(api_version, team, 'list'))
    data['data'].append(getMonthData(api_version, team, 'commits'))
    data['data'].append(getMonthData(api_version, team, 'commitlines'))
    
    return HttpResponse(json.dumps(data))

def monthTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    logger.info("Month Top N Function Called")
    metricname = helper.identifyMetric(team, metric)
    data = {'team' : team}
    data['data'] = {'metric' : metric}
    if metric == 'list':
        data['data']['data'] = [helper.monthTopNList(team,m,n) for m in metricname]
    elif metric == 'commits':
        data['data']['data'] = [helper.monthTopNCommits(team,m,n) for m in metricname]
    elif metric == 'commitlines':
        data['data']['data'] = [helper.monthTopNCommitLines(team,m,n) for m in metricname]
    return HttpResponse(json.dumps(data))

