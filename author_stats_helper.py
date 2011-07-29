#!/usr/bin/python
# Copyright 2011: Andreas Tille <tille@debian.org>
# License: GPL
# Takes a project mailing list name and a number of top authors
# Creates a text file with the statistics table

NMAX=30

from sys import argv, stderr, exit

if len(argv) != 3 :
    print >>stderr, "Usage: %s <project> <no authors>" % (argv[0])
    exit(-1)

project = argv[1]

PORT=5441
DEFAULTPORT=5432
DB='teammetrics'

import psycopg2
import re

try:
    conn = psycopg2.connect(database=DB)
    # conn = psycopg2.connect(host="localhost",port=PORT,user="guest",database=DB)
except psycopg2.OperationalError:
    try:
        conn = psycopg2.connect(host="localhost",port=DEFAULTPORT,user="guest",database=DB)
    except psycopg2.OperationalError:
	conn = psycopg2.connect(host="127.0.0.1",port=DEFAULTPORT,user="guest",database=DB)

curs = conn.cursor()

def RowDictionaries(cursor):
    """Return a list of dictionaries which specify the values by their column names"""

    description = cursor.description
    if not description:
        # even if there are no data sets to return the description should contain the table structure.  If not something went
        # wrong and we return NULL as to represent a problem
        return NULL
    if cursor.rowcount <= 0:
        # if there are no rows in the cursor we return an empty list
        return []

    data = cursor.fetchall()
    result = []

    for row in data:
        resultrow = {}
        i = 0
        for dd in description:
            resultrow[dd[0]] = row[i]
            i += 1
        result.append(resultrow)
    return result

crosstab_missing_re  = re.compile(".* crosstab.*")

query = "SELECT replace(author,' ','_') AS author FROM author_names_of_list('%s', %i) AS (author text);" % (project, NMAX)
# print query
curs.execute(query)

print ' year',
nuploaders = 0
for row in curs.fetchall():
    print '\t' + re.sub('^(.*_\w)[^_]*$', '\\1', row[0]),
    nuploaders += 1
print ''

typestring = 'year text'
for i in range(nuploaders):
    typestring = typestring + ', upl' + str(i+1) + ' int'
query = """SELECT *
	FROM 
	crosstab(
             'SELECT year AS row_name, name AS bucket, count AS value
                     FROM author_per_year_of_list(''%s'', %i) AS (name text, year int, count int)',
             'SELECT * FROM author_names_of_list(''%s'', %i) AS (category text)'

        ) As (%s)
""" % (project, nuploaders, project, nuploaders, typestring)

try:
    # print query
    curs.execute(query)
except psycopg2.ProgrammingError, err:
    if crosstab_missing_re.match(str(err)):
        print >>stderr, """Please do
	psql udd < /usr/share/postgresql/<pgversion>/contrib/tablefunc.sql
before calling this program."""
    else:
        print >>stderr, "To few authors in %s list.\n%s" % (project, err)
    exit(-1)
for row in curs.fetchall():
    print ' ' + row[0] ,
    for v in row[1:]:
        if v:
            print '\t' + str(v),
        else:
            print '\t0',
    print ''


