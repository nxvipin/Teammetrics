from web.models import database

cur = database.connect()

def monthData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       extract(MONTH
                               FROM archive_date) AS MONTH,
                       count(*)
                FROM listarchives
                WHERE project=%s
                AND archive_date >= date(%s) 
                AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR, MONTH
                ORDER BY YEAR, MONTH; """
    cur.execute(sql,(team,startdate,enddate))
    return cur.fetchall()

def annualData(team, startdate='epoch', enddate='now'):
    """
    Return annual liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       count(*)
                FROM listarchives
                WHERE project = %s
                AND archive_date >= date(%s) 
                AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR
                ORDER BY YEAR; """
    cur.execute(sql,(team,startdate,enddate))
    return cur.fetchall()

def monthTopN(team, n, startdate='epoch', enddate='now'):
    """
    Return monthly liststat data of all time top 'N' members.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       extract(MONTH
                               FROM archive_date) AS MONTH,
                       name,
                       count(*)
                FROM listarchives
                WHERE project=%s
                    AND name IN
                        (SELECT name
                         FROM listarchives
                         WHERE project = %s
                         AND archive_date >= date(%s) 
                         AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                         GROUP BY name
                         ORDER BY count(*) DESC LIMIT %s)
                AND archive_date >= date(%s) 
                AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR,MONTH, name
                ORDER BY YEAR, MONTH, COUNT DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()

def annualTopN(team, n, startdate='epoch', enddate='now'):
    """
    Returns annual liststat data for top 'N' members of a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       name,
                       count(*)
                FROM listarchives
                WHERE project=%s
                    AND name IN
                        (SELECT name
                         FROM listarchives
                         WHERE project = %s
                         AND archive_date >= date(%s) 
                         AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                         GROUP BY name
                         ORDER BY count(*) DESC LIMIT %s)
                AND archive_date >= date(%s) 
                AND archive_date <= date(%s) + interval '1 month' - interval '1 day'
                GROUP BY YEAR,name
                ORDER BY YEAR, COUNT DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()
