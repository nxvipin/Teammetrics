from web.models import database
from web.lib import log

cur = database.connect()
logger = log.get(__name__)

def monthData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       extract(MONTH
                               FROM commit_date) AS MONTH,
                       count(*)
                FROM commitstat
                WHERE project=%s
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR, MONTH
                ORDER BY YEAR; """
    cur.execute(sql,(team, startdate, enddate))
    return cur.fetchall()

def annualData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       count(*)
                FROM commitstat
                WHERE project=%s
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR
                ORDER BY YEAR; """
    cur.execute(sql,(team, startdate, enddate))
    return cur.fetchall()

def monthTopN(team, n, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for Top 'N' members a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       extract(MONTH
                               FROM commit_date) AS MONTH,
                       name,
                       count(*)
                FROM commitstat
                WHERE project=%s
                    AND name IN (
                    SELECT name
                    FROM commitstat WHERE project = %s
                    AND commit_date >= date(%s) 
                    AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY name
                ORDER BY count(*) DESC LIMIT %s)
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR, MONTH, name
                ORDER BY YEAR, MONTH, COUNT DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()

def annualTopN(team, n, startdate='epoch', enddate='now'):
    """
    Returns annual liststat data for Top 'N' members a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       name,
                       count(*)
                FROM commitstat
                WHERE project=%s
                    AND name IN (
                    SELECT name
                    FROM commitstat WHERE project = %s
                    AND commit_date >= date(%s) 
                    AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY name
                ORDER BY count(*) DESC LIMIT %s)
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR, name
                ORDER BY YEAR, COUNT DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()

def get(team, startdate='epoch', enddate='now', n=None, datascale='month'):
    """
    Unified interface to extract data from the database.
    """
    logger.info('commitstat.get called')
    if datascale == 'month':
        if n is None:
            logger.info('month')
            return monthData(team, startdate, enddate)
        else:
            logger.info('month n')
            return monthTopN(team, n, startdate, enddate)
    elif datascale == 'annual':
        if n is None:
            logger.info('annual')
            return annualData(team, startdate, enddate)
        else:
            logger.info('annual n')
            return annualTopN(team, n, startdate, enddate)
    else:
        return None
