from web.models import database
cur = database.connect()
def month(team):
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



