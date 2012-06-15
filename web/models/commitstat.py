from web.models import database

cur = database.connect()

def monthData(team):
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
                GROUP BY YEAR, MONTH
                ORDER BY YEAR; """
    cur.execute(sql,(team,))
    return cur.fetchall()

def annualData(team):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       count(*)
                FROM commitstat
                WHERE project=%s
                GROUP BY YEAR
                ORDER BY YEAR; """
    cur.execute(sql,(team,))
    return cur.fetchall()

def monthTopN(team, n):
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
                GROUP BY name
                ORDER BY count(*) DESC LIMIT %s)
                GROUP BY YEAR, MONTH, name
                ORDER BY YEAR, MONTH, COUNT DESC; """
    cur.execute(sql,(team, team, n))
    return cur.fetchall()

def annualTopN(team, n):
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
                GROUP BY name
                ORDER BY count(*) DESC LIMIT %s)
                GROUP BY YEAR, name
                ORDER BY YEAR, COUNT DESC; """
    cur.execute(sql,(team, team, n))
    return cur.fetchall()
