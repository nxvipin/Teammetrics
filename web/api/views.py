from django.http import HttpResponse
from web.lib import log, lib
from web.api import helper
import json

logger = log.get(__name__)

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def month(request, api_version, team, metric):
    data = helper.getData(team, metric, n=None, datascale='month')
    startdate, enddate = lib.dateRange(request)
    data = helper.getMonthData(team, metric, startdate, enddate)
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def monthAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getData(team, 'list', n=None, datascale='month'))
    data['data'].append(helper.getData(team, 'commits', n=None, datascale='month'))
    data['data'].append(helper.getData(team, 'commitlines', n=None, datascale='month'))
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def monthTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    data = helper.getData(team, metric, n=n, datascale='month')
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annual(request, api_version, team, metric):
    data = helper.getData(team, metric, n=None, datascale='annual')
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annualAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getData(team, 'list', n=None, datascale='annual'))
    data['data'].append(helper.getData(team, 'commits', n=None, datascale='annual'))
    data['data'].append(helper.getData(team, 'commitlines', n=None, datascale='annual'))
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annualTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    data = helper.getData(team, metric, n=n, datascale='annual')
    data['team'] = team
    return data
