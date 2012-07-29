from web.models import database
from web.lib import log

cur = database.connect('udd')
logger = log.get(__name__)

def monthData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """    SELECT uh.year, uh.month, COUNT(*)::int FROM
                    (SELECT source, EXTRACT(year FROM date)::int AS year, EXTRACT(month FROM date)::int AS month, changed_by_email
                       FROM upload_history
                      WHERE nmu = 'f' and date >= date(%s) and date <= date(%s)
                    ) uh
                    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                    JOIN (SELECT * FROM carnivore_names
                           WHERE id IN (SELECT idupl FROM active_uploader_ids_of_pkggroup(%s, 35) AS (idupl int, count int))
                    )  cn ON ce.id    = cn.id
                    JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                   WHERE source IN (           -- source packages that are maintained by the team
                      SELECT DISTINCT source FROM upload_history
                      WHERE maintainer_email = %s
                        AND nmu = 'f'
                     )
                     AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
                      SELECT DISTINCT ce.email FROM upload_history uh
                        JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                       WHERE maintainer_email = %s
                     )
                     AND cn.name = cnp.name
                   GROUP BY  uh.year, uh.month
                   ORDER BY year, month, count DESC"""
    cur.execute(sql,(startdate, enddate, team, team, team))
    return cur.fetchall()

def annualData(team, startdate='epoch', enddate='now'):
    """
    Return annual liststat data for a given team.
    """
    sql = """   SELECT uh.year, COUNT(*)::int FROM
                    (SELECT source, EXTRACT(year FROM date)::int AS year,  changed_by_email
                       FROM upload_history
                      WHERE nmu = 'f' and date >= date(%s) and date <= date(%s)
                    ) uh
                    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                    JOIN (SELECT * FROM carnivore_names
                           WHERE id IN (SELECT idupl FROM active_uploader_ids_of_pkggroup(%s, 35) AS (idupl int, count int))
                    )  cn ON ce.id    = cn.id
                    JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                   WHERE source IN (           -- source packages that are maintained by the team
                      SELECT DISTINCT source FROM upload_history
                      WHERE maintainer_email = %s
                        AND nmu = 'f'
                     )
                     AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
                      SELECT DISTINCT ce.email FROM upload_history uh
                        JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                       WHERE maintainer_email = %s
                     )
                     AND cn.name = cnp.name
                   GROUP BY uh.year
                   ORDER BY year, count DESC"""
    cur.execute(sql,(startdate, enddate, team, team, team))
    return cur.fetchall()

def monthTopN(team, n, startdate='epoch', enddate='now'):
    """
    Return monthly liststat data of all time top 'N' members.
    """
    sql = """   SELECT  uh.year, uh.month, cn.name, COUNT(*)::int FROM
                (SELECT source, EXTRACT(year FROM date)::int AS year, EXTRACT(month FROM date)::int AS month, changed_by_email
                   FROM upload_history
                  WHERE nmu = 'f' and date >= date(%s) and date <= date(%s)
                ) uh
                JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                JOIN (SELECT * FROM carnivore_names
                       WHERE id IN (SELECT idupl FROM active_uploader_ids_of_pkggroup(%s, %s) AS (idupl int, count int))
                )  cn ON ce.id    = cn.id
                JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
               WHERE source IN (           -- source packages that are maintained by the team
                  SELECT DISTINCT source FROM upload_history
                  WHERE maintainer_email = %s
                    AND nmu = 'f'
                 )
                 AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
                  SELECT DISTINCT ce.email FROM upload_history uh
                    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                   WHERE maintainer_email = %s
                 )
                 AND cn.name = cnp.name
                 AND cn.name in (SELECT name FROM active_uploader_per_year_of_pkggroup(%s, 1000) AS (name text, _ int, count int) group by name order by sum(count) desc limit %s)
               GROUP BY cn.name, uh.year, uh.month
               ORDER BY year, month, count DESC, cn.name """
    cur.execute(sql,(startdate, enddate, team, n, team, team, team, n))
    return cur.fetchall()

def annualTopN(team, n, startdate='epoch', enddate='now'):
    """
    Returns annual liststat data for top 'N' members of a given team.
    """
    sql = """ SELECT uh.year, cn.name, COUNT(*)::int FROM
                (SELECT source, EXTRACT(year FROM date)::int AS year, changed_by_email
                   FROM upload_history
                  WHERE nmu = 'f' and date >= date(%s) and date <= date(%s)
                ) uh
                JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                JOIN (SELECT * FROM carnivore_names
                       WHERE id IN (SELECT idupl FROM active_uploader_ids_of_pkggroup(%s, %s) AS (idupl int, count int))
                )  cn ON ce.id    = cn.id
                JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
               WHERE source IN (           -- source packages that are maintained by the team
                  SELECT DISTINCT source FROM upload_history
                  WHERE maintainer_email = %s
                    AND nmu = 'f'
                 )
                 AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
                  SELECT DISTINCT ce.email FROM upload_history uh
                    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                   WHERE maintainer_email = %s
                 )
                 AND cn.name = cnp.name
                 AND cn.name in (SELECT name FROM active_uploader_per_year_of_pkggroup(%s, 1000) AS (name text, _ int, count int) group by name order by sum(count) desc limit %s)
               GROUP BY cn.name, uh.year
               ORDER BY year, count DESC, cn.name"""
    cur.execute(sql,(startdate, enddate, team, n, team, team, team, n))
    return cur.fetchall()

def get(team, startdate='epoch', enddate='now', n=None, datascale='month'):
    """
    Unified interface to extract data from the database.
    """
    logger.info('listarchives.get called')
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

def getTopN(team, startdate='epoch', enddate='now', n=10):
    """
    Returns a list of Top N members of a team.
    """
    sql = """   SELECT name,
                       sum(COUNT) AS SUM
                FROM active_uploader_per_year_of_pkggroup(%s, 1000) AS (name text, _ int, COUNT int)
                GROUP BY name
                ORDER BY SUM DESC limit %s"""
    cur.execute(sql,(team,n))
    return cur.fetchall()
