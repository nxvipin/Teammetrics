PORT=5441
DEFAULTPORT=5432
DB='teammetrics'

import psycopg2
import simplejson
import re

try:
    conn = psycopg2.connect(database=DB)
    # conn = psycopg2.connect(host="localhost",port=PORT,user="guest",database=DB)
except psycopg2.OperationalError:
    try:
        conn = psycopg2.connect(host="localhost",port=DEFAULTPORT,user="guest",database=DB)
    except psycopg2.OperationalError:
      conn = psycopg2.connect(host="127.0.0.1",port=PORT,user="guest",database=DB)

cur = conn.cursor()

sql = \
"select \
    extract(year from archive_date) as year,  \
    extract(month from archive_date) as month, \
    count(*) \
from \
    listarchives \
where \
        extract(year from archive_date) in  \
            (select \
                distinct extract(year from archive_date) \
            from \
                listarchives \
            where \
                    project = %s) \
    and \
        project=%s \
    and \
        name = %s \
group by \
    year, \
    month \
order by \
    year;"

def checkKeyExists(dlist, key, value):
    for d in dlist:
        if d[key]==value:
            print dlist.index(d)
            return dlist.index(d)
    return -1

data = ('teammetrics-discuss', 'teammetrics-discuss', 'Sukhbir Singh')
cur.execute(sql,data)
a = cur.fetchall()

b=dict()
b["name"] = data[2]
b["data"] = []
d = -1
for i in a:
    print d
    d=checkKeyExists(b["data"],"year",int(float(i[0])))
    print d
    if d == -1 :
        b["data"].append({"year":int(float(i[0]))})
        d=len(b["data"])-1
    if not b["data"][d].has_key("data"):
        b["data"][d]["data"]=[]
    b["data"][d]["data"].append({"month":int(float(i[1])),"data":int(float(i[2]))})

import simplejson
print simplejson.dumps(b)



#Data Caching. Premature optimization. Ignore.
#class cache:
#    store={}
#    def __init__(self, dlist):
#        self.dlist = dlist
#    def get(self, key, val):
#        if self.store.has_key(val):
#            return self.store[val]
#        else:
#            for d in self.dlist:
#                if d[key]==val:
#                    self.store[val]=self.dlist.index(d)
#                    break
#            if not self.store.has_key(val):
#                self.store[key]=len(self.store)
#            return self.store[key]
