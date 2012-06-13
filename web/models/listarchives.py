from web.models import database

cur = database.connect()

def monthData(team):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """ select extract(year from archive_date) as year, 
                    extract(month from archive_date) as month, 
                    count(*) 
                from 
                    listarchives 
                where 
                    extract(year from archive_date) in 
                      (select 
                            distinct extract(year from archive_date) 
                        from 
                            listarchives 
                        where 
                           project = %s) 
                and 
                    project=%s 
                group by 
                    year, 
                    month 
                order by 
                    year;"""
    cur.execute(sql,(team,team))
    return cur.fetchall()

def annualData(team):
    """
    Return annual liststat data for a given team.
    """
    sql = """   SELECT extract(YEAR
                               FROM archive_date) AS YEAR,
                       count(*)
                FROM listarchives
                WHERE project = '%s'
                GROUP BY YEAR
                ORDER BY YEAR; """
    cur.execute(sql,(team))
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
                WHERE project='%s'
                    AND name IN
                        (SELECT name
                         FROM listarchives
                         WHERE project = '%s'
                         GROUP BY name
                         ORDER BY count(*) DESC LIMIT %d)
                GROUP BY YEAR,name
                ORDER BY YEAR, COUNT DESC; """
    cur.execute(sql,(team,team,n))
    return cur.fetchall()
