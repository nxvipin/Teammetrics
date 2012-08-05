from web.models import database
from web.lib import log

cur = database.connect('udd')
logger = log.get(__name__)

def monthData(team, startdate='epoch', enddate='now'):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """    SELECT db.year,
                           db.month,
                           COUNT(*)::int
                    FROM
                      (SELECT id, SOURCE, EXTRACT(YEAR
                                                  FROM last_modified)::int AS YEAR,
                                          EXTRACT(MONTH
                                                  FROM last_modified)::int AS MONTH,
                                          done_email
                       FROM archived_bugs
                       UNION SELECT id, SOURCE, EXTRACT(YEAR
                                                        FROM last_modified)::int AS YEAR,
                                                EXTRACT(MONTH
                                                        FROM last_modified)::int AS MONTH,
                                                done_email
                       FROM bugs
                       WHERE status = 'done'
                         AND last_modified >= date(%s)
                         AND last_modified <= date(%s) ) db
                    JOIN carnivore_emails ce ON ce.email = db.done_email
                    JOIN
                      (SELECT *
                       FROM carnivore_names
                       WHERE id IN
                           (SELECT idupl
                            FROM bug_closer_ids_of_pkggroup(%s, 1000) AS (idupl int, COUNT int)) ) cn ON ce.id = cn.id
                    JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                    WHERE SOURCE IN (-- source packages that are maintained by the team

                                     SELECT DISTINCT SOURCE
                                     FROM upload_history
                                     WHERE maintainer_email = %s
                                       AND nmu = 'f')
                      AND done_email IN (-- email of uploaders who at least once uploaded on behalf of the team

                                         SELECT DISTINCT ce.email
                                         FROM upload_history uh
                                         JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                                         WHERE maintainer_email = %s )
                      AND cn.name = cnp.name
                    GROUP BY db.YEAR, db.MONTH
                    ORDER BY YEAR, MONTH, COUNT DESC
    """
    cur.execute(sql,(startdate, enddate, team, team, team))
    return cur.fetchall()

def annualData(team, startdate='epoch', enddate='now'):
    """
    Return annual liststat data for a given team.
    """
    sql = """   SELECT db.year,
                       COUNT(*)::int
                FROM
                  (SELECT id, SOURCE, EXTRACT(YEAR
                                              FROM last_modified)::int AS YEAR,
                                      done_email
                   FROM archived_bugs
                   UNION SELECT id, SOURCE, EXTRACT(YEAR
                                                    FROM last_modified)::int AS YEAR,
                                            done_email
                   FROM bugs
                   WHERE status = 'done'
                     AND last_modified >= date(%s)
                     AND last_modified <= date(%s) ) db
                JOIN carnivore_emails ce ON ce.email = db.done_email
                JOIN
                  (SELECT *
                   FROM carnivore_names
                   WHERE id IN
                       (SELECT idupl
                        FROM bug_closer_ids_of_pkggroup(%s, 1000) AS (idupl int, COUNT int)) ) cn ON ce.id = cn.id
                JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                WHERE SOURCE IN (-- source packages that are maintained by the team

                                 SELECT DISTINCT SOURCE
                                 FROM upload_history
                                 WHERE maintainer_email = %s
                                   AND nmu = 'f' )
                  AND done_email IN (-- email of uploaders who at least once uploaded on behalf of the team

                                     SELECT DISTINCT ce.email
                                     FROM upload_history uh
                                     JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                                     WHERE maintainer_email = %s )
                  AND cn.name = cnp.name
                GROUP BY db.YEAR
                ORDER BY YEAR, COUNT DESC"""
    cur.execute(sql,(startdate, enddate, team, team, team))
    return cur.fetchall()

def monthTopN(team, n, startdate='epoch', enddate='now'):
    """
    Return monthly liststat data of all time top 'N' members.
    """
    sql = """   SELECT db.year,
                       db.month,
                       cn.name,
                       COUNT(*)::int
                FROM
                  (SELECT id, SOURCE, EXTRACT(YEAR
                                              FROM last_modified)::int AS YEAR,
                                      EXTRACT(MONTH
                                              FROM last_modified)::int AS MONTH,
                                      done_email
                   FROM archived_bugs
                   UNION SELECT id, SOURCE, EXTRACT(YEAR
                                                    FROM last_modified)::int AS YEAR,
                                            EXTRACT(MONTH
                                                    FROM last_modified)::int AS MONTH,
                                            done_email
                   FROM bugs
                   WHERE status = 'done'
                     AND last_modified >= date(%s)
                     AND last_modified <= date(%s) ) db
                JOIN carnivore_emails ce ON ce.email = db.done_email
                JOIN
                  (SELECT *
                   FROM carnivore_names
                   WHERE id IN
                       (SELECT idupl
                        FROM bug_closer_ids_of_pkggroup(%s, %s) AS (idupl int, COUNT int)) ) cn ON ce.id = cn.id
                JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                WHERE SOURCE IN (-- source packages that are maintained by the team

                                 SELECT DISTINCT SOURCE
                                 FROM upload_history
                                 WHERE maintainer_email = %s
                                   AND nmu = 'f' )
                  AND done_email IN (-- email of uploaders who at least once uploaded on behalf of the team

                                     SELECT DISTINCT ce.email
                                     FROM upload_history uh
                                     JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                                     WHERE maintainer_email = %s )
                  AND cn.name = cnp.name
                  AND cn.name IN
                    (SELECT name
                     FROM bug_closer_per_year_of_pkggroup(%s, 1000) AS (name text, YEAR int, COUNT int)
                     GROUP BY name
                     ORDER BY sum(COUNT) DESC LIMIT %s)
                GROUP BY db.YEAR, db.MONTH, cn.name
                ORDER BY YEAR, MONTH, COUNT DESC
        
    """
    cur.execute(sql,(startdate, enddate, team, n, team, team, team, n))
    return cur.fetchall()

def annualTopN(team, n, startdate='epoch', enddate='now'):
    """
    Returns annual liststat data for top 'N' members of a given team.
    """
    sql = """    SELECT db.year,
                       cn.name,
                       COUNT(*)::int
                FROM
                  (SELECT id, SOURCE, EXTRACT(YEAR
                                              FROM last_modified)::int AS YEAR,
                                      done_email
                   FROM archived_bugs
                   UNION SELECT id, SOURCE, EXTRACT(YEAR
                                                    FROM last_modified)::int AS YEAR,
                                            done_email
                   FROM bugs
                   WHERE status = 'done'
                     AND last_modified >= date(%s)
                     AND last_modified <= date(%s) ) db
                JOIN carnivore_emails ce ON ce.email = db.done_email
                JOIN
                  (SELECT *
                   FROM carnivore_names
                   WHERE id IN
                       (SELECT idupl
                        FROM bug_closer_ids_of_pkggroup(%s, %s) AS (idupl int, COUNT int)) ) cn ON ce.id = cn.id
                JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
                WHERE SOURCE IN (-- source packages that are maintained by the team

                                 SELECT DISTINCT SOURCE
                                 FROM upload_history
                                 WHERE maintainer_email = %s
                                   AND nmu = 'f' )
                  AND done_email IN (-- email of uploaders who at least once uploaded on behalf of the team

                                     SELECT DISTINCT ce.email
                                     FROM upload_history uh
                                     JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
                                     WHERE maintainer_email = %s )
                  AND cn.name = cnp.name
                  AND cn.name IN
                    (SELECT name
                     FROM bug_closer_per_year_of_pkggroup(%s, 1000) AS (name text, YEAR int, COUNT int)
                     GROUP BY name
                     ORDER BY sum(COUNT) DESC LIMIT %s)
                GROUP BY db.YEAR, cn.name
                ORDER BY YEAR, COUNT DESC"""
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
                       sum(COUNT)
                FROM bug_closer_per_year_of_pkggroup(%s, 1000) AS (name text, YEAR int, COUNT int)
                GROUP BY name
                ORDER BY sum(COUNT) DESC LIMIT %s"""
    cur.execute(sql,(team,n))
    return cur.fetchall()
