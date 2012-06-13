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
                WHERE project='teammetrics'
                GROUP BY YEAR, MONTH
                ORDER BY YEAR; """
    cur.execute(sql,(team,team))
    return cur.fetchall()



