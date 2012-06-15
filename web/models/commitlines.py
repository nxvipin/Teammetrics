from web.models import database

cur = database.connect()

def monthData(team,):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       extract(MONTH
                               FROM commit_date) AS MONTH,
                       sum(lines_inserted) AS LINES_INSERTED,
                       sum(lines_deleted) AS LINES_DELETED
                FROM commitstat
                WHERE project=%s
                GROUP BY YEAR, MONTH
                ORDER BY YEAR, MONTH; """
    cur.execute(sql,(team,))
    return cur.fetchall()

def annualData(team,):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       sum(lines_inserted) AS LINES_INSERTED,
                       sum(lines_deleted) AS LINES_DELETED
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
                       sum(lines_inserted) AS LINES_INSERTED,
                       sum(lines_deleted) AS LINES_DELETED
                FROM commitstat
                WHERE project=%s
                  AND name IN
                    (SELECT name
                     FROM commitstat
                     WHERE project = %s
                       AND lines_inserted IS NOT NULL
                       AND lines_deleted IS NOT NULL
                     GROUP BY name
                     ORDER BY sum(lines_inserted)+sum(lines_deleted) DESC LIMIT %s)
                  AND lines_inserted IS NOT NULL
                  AND lines_deleted IS NOT NULL
                GROUP BY YEAR, MONTH, name
                ORDER BY YEAR, MONTH, LINES_INSERTED DESC,LINES_DELETED DESC; """
    cur.execute(sql,(team, team, n))
    return cur.fetchall()

def annualTopN(team, n):
    """
    Returns annual liststat data for Top 'N' members a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       name,
                       sum(lines_inserted) AS LINES_INSERTED,
                       sum(lines_deleted) AS LINES_DELETED
                FROM commitstat
                WHERE project=%s
                  AND name IN
                    (SELECT name
                     FROM commitstat
                     WHERE project = %s
                       AND lines_inserted IS NOT NULL
                       AND lines_deleted IS NOT NULL
                     GROUP BY name
                     ORDER BY sum(lines_inserted)+sum(lines_deleted) DESC LIMIT %s)
                  AND lines_inserted IS NOT NULL
                  AND lines_deleted IS NOT NULL
                GROUP BY YEAR, name
                ORDER BY YEAR, LINES_INSERTED DESC,LINES_DELETED DESC; """
    cur.execute(sql,(team, team, n))
    return cur.fetchall()
