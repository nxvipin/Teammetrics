from django.http import HttpResponse
from web.models import listarchives
from web.lib import metrics

import json

def _checkKeyExists(dlist, key, value):
    for d in dlist:
        if d[key]==value:
            print dlist.index(d)
            return dlist.index(d)
    return -1

def _monthList(team, mlist):
    mdata=listarchives.month(mlist)
    data=dict()
    data['mailing-list'] = mlist
    data['data'] = []
    for i in mdata:
        d = _checkKeyExists(data['data'],'year',int(float(i[0])))
        if d == -1 :
            data['data'].append({'year':int(float(i[0]))})
            d=len(data['data'])-1
        if not data['data'][d].has_key('data'):
            data['data'][d]['data']=[]
        data['data'][d]['data'].append({'month':int(float(i[1])),'data':int(float(i[2]))})
    return data

def month(request, api_version, team, metric):
    """
    Returns monthly data as JSON for a given team and metric.
    """
    mlist = metrics.get(team,metric)
    data = {'team' : team}
    data['data'] = {'metric' : metric}
    if metric == 'list':
        data['data']['data'] = [_monthList(team,m) for m in mlist]
    return HttpResponse(json.dumps(data))
