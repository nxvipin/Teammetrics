from flask import request
from web.lib import log, lib
from web.api import helper
import json

logger = log.get(__name__)

@lib.jsonify
@lib.metricCheck
@lib.teamCheck
@lib.versionCheck
def metric(api_version, team, metric):
    n = request.args.get('n', None)
    datascale = request.args.get('scale','month')
    data = helper.getData(team, metric, n=n, datascale=datascale)
    data['team'] = team
    return data

@lib.jsonify
@lib.metricCheck
@lib.teamCheck
@lib.versionCheck
def metric_all(api_version, team):
    n = request.args.get('n', None)
    datascale = request.args.get('scale','month')
    data = {}
    data['team'] = team
    data['data'] = []
    data['data'].append(helper.getData(team, 'list', n=n, datascale=datascale))
    data['data'].append(helper.getData(team, 'commits', n=n, datascale=datascale))
    data['data'].append(helper.getData(team, 'commitlines', n=n, datascale=datascale))
    return data
