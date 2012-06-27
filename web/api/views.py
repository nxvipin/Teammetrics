from django.http import HttpResponse
from web.lib import log, lib
from web.api import helper
import json

logger = log.get(__name__)

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def month(request, api_version, team, metric):
    data = helper.getMonthData(team, metric)
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def monthAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getMonthData(team, 'list'))
    data['data'].append(helper.getMonthData(team, 'commits'))
    data['data'].append(helper.getMonthData(team, 'commitlines'))
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def monthTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    data = helper.getMonthTopNData(team, metric, n)
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annual(request, api_version, team, metric):
    data = helper.getAnnualData(team, metric)
    data['team'] = team
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annualAll(request, api_version, team):
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getAnnualData(team, 'list'))
    data['data'].append(helper.getAnnualData(team, 'commits'))
    data['data'].append(helper.getAnnualData(team, 'commitlines'))
    return data

@lib.respond('JSON')
@lib.jsonify
@lib.versionCheck
def annualTopN(request, api_version, team, metric, n):
    """
    Returns monthly data for top N members.
    """
    data = helper.getAnnualTopNData(team, metric, n)
    data['team'] = team
    return data
