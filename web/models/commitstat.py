from web.models import database
cur = database.connect()
def month(team):
    """
    Returns monthly liststat data for a given team.
    """
    sql = """ select extract(year from commit_date) as year, 
                    extract(month from commit_date) as month, 
                    count(*) 
                from 
                    commitstat 
                where 
                    extract(year from commit_date) in 
                      (select 
                            distinct extract(year from commit_date) 
                        from 
                            commitstat 
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



