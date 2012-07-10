from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
import helper
import web.lib.metrics as metrics

def index(request):
    t = loader.get_template('base.html')
    c = Context({
        'title': 'Debian Team Activity Metrics'
    })
    return HttpResponse(t.render(c))

def getData(request):
    team = request.GET.get('team','')
    metric = request.GET.get('metric','')
    if team is not '' and metric is not '':
        return HttpResponseRedirect("/%s/%s/"%(team,metric))

def teamdata(request, team, metric):
    teamname = metrics.identify(team,metric)
    metricname = metrics.name(metric)
    namelist = helper.getTopNNames(teamname[0], metric)
    t = loader.get_template('base.html')
    c = Context({
        'metricname': metricname,
        'teamname': teamname[0],
        'namelist': namelist
    })
    return HttpResponse(t.render(c))
