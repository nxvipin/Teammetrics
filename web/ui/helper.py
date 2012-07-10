from web.models import listarchives, commitstat, commitlines

def getTopNNames(team, metric, n=10):
    if metric == 'list':
        return listarchives.getTopN(team)
    elif metric == 'commits':
        return commitstat.getTopN(team)
    elif metric == 'commitlines':
        return commitlines.getTopN(team)
    else:
        return []
