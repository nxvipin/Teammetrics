from django.http import HttpResponse
from web.lib import log
from web.api import helper
import json

logger = log.get(__name__)



def month(request, api_version, team, metric):
    data = helper.getMonthData(api_version, team, metric)
    data['team'] = team
    return HttpResponse(json.dumps(data))

def monthAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getMonthData(api_version, team, 'list'))
    data['data'].append(helper.getMonthData(api_version, team, 'commits'))
    data['data'].append(helper.getMonthData(api_version, team, 'commitlines'))
    return HttpResponse(json.dumps(data))

def monthTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    data = helper.getMonthTopNData(api_version, team, metric)
    data['team'] = team
    return HttpResponse(json.dumps(data))

