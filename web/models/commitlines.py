from web.models import database

cur = database.connect()

def monthData(team, startdate='epoch', enddate='now'):
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
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day
                GROUP BY YEAR, MONTH
                ORDER BY YEAR, MONTH; """
    cur.execute(sql,(team, startdate, enddate))
    return cur.fetchall()

def annualData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM commit_date) AS YEAR,
                       sum(lines_inserted) AS LINES_INSERTED,
                       sum(lines_deleted) AS LINES_DELETED
                FROM commitstat
                WHERE project=%s
                AND commit_date >= date(%s) 
                AND commit_date <= date(%s) + interval '1 month' - interval '1 day
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
                       AND commit_date >= date(%s) 
                       AND commit_date <= date(%s) + interval '1 month' - interval '1 day
                     GROUP BY name
                     ORDER BY sum(lines_inserted)+sum(lines_deleted) DESC LIMIT %s)
                  AND lines_inserted IS NOT NULL
                  AND lines_deleted IS NOT NULL
                  AND commit_date >= date(%s) 
                  AND commit_date <= date(%s) + interval '1 month' - interval '1 day
                GROUP BY YEAR, MONTH, name
                ORDER BY YEAR, MONTH, LINES_INSERTED DESC,LINES_DELETED DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()

def annualTopN(team, n, startdate='epoch', enddate='now'):
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
                       AND commit_date >= date(%s) 
                       AND commit_date <= date(%s) + interval '1 month' - interval '1 day
                     GROUP BY name
                     ORDER BY sum(lines_inserted)+sum(lines_deleted) DESC LIMIT %s)
                  AND lines_inserted IS NOT NULL
                  AND lines_deleted IS NOT NULL
                  AND commit_date >= date(%s) 
                  AND commit_date <= date(%s) + interval '1 month' - interval '1 day
                GROUP BY YEAR, name
                ORDER BY YEAR, LINES_INSERTED DESC,LINES_DELETED DESC; """
    cur.execute(sql,(team, team, startdate, enddate, n, startdate, enddate))
    return cur.fetchall()
