from flask import render_template, redirect, request, url_for
import helper
import web.lib.metrics as metrics
from web.lib import log

logger = log.get(__name__)

def index():
    logger.info('index')
    return render_template('base.html')

def get_data():
    team = request.args.get('team','teammetrics')
    metric = request.args.get('metric','list')
    return redirect(url_for('teamdata', team=team, metric=metric), 301)

def teamdata(team, metric):
    logger.info('teamdata')
    if not metrics.check_team_exists(team):
        msg = "No such team or data not available."
        return render_template('error.html', error_msg = msg)
    if not metrics.check_metric_exist(team, metric):
        msg = "No such metric or data not available."
        return render_template('error.html', error_msg = msg)
    teamname = metrics.identify(team,metric)
    metricname = metrics.name(metric)
    namelist = helper.getTopNNames(teamname[0], metric)
    teamlist = metrics.get_all_teams()
    if metric == 'uploads':
        teamname = metrics.identify(team,'uploadsname')
        print metrics.identify(team,'uploadsname')
    elif metric == 'bugs':
        teamname = metrics.identify(team,'bugsname')
        print metrics.identify(team,'bugssname')
    return render_template('main.html',
                            teamname=teamname[0],
                            namelist=namelist,
                            metric=metric,
                            metricname=metricname,
                            teamlist=teamlist)

#TODO
def teamdatajs(request, team, metric):
    teamname = metrics.identify(team,metric)
    metricname = metrics.name(metric)
    namelist = helper.getTopNNames(teamname[0], metric)
    if metric == 'uploads':
        teamname = metrics.identify(team,'uploadsname')
        print metrics.identify(team,'uploadsname')
    t = loader.get_template('js.html')
    c = Context({
        'metric': metric,
        'team': team,
        'metricname': metricname,
        'teamname': teamname[0],
        'namelist': namelist
    })
    return HttpResponse(t.render(c))
