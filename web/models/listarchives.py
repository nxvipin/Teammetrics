from web.models import database

cur = database.connect()

def monthData(team):
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
                GROUP BY YEAR, MONTH
                ORDER BY YEAR; """
    cur.execute(sql,(team,))
    return cur.fetchall()

def annualData(team):
    """
    Return annual liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       count(*)
                FROM listarchives
                WHERE project = %s
                GROUP BY YEAR
                ORDER BY YEAR; """
    cur.execute(sql,(team,))
    return cur.fetchall()

def monthTopN(team, n):
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
                         GROUP BY name
                         ORDER BY count(*) DESC LIMIT %d)
                GROUP BY YEAR,MONTH, name
                ORDER BY YEAR, MONTH, COUNT DESC; """
    cur.execute(sql,(team, team, n))
    return cur.fetchall()

def annualTopN(team, n):
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
                         GROUP BY name
                         ORDER BY count(*) DESC LIMIT %d)
                GROUP BY YEAR,name
                ORDER BY YEAR, COUNT DESC; """
    cur.execute(sql,(team,team,n))
    return cur.fetchall()
