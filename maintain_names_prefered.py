#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2011: Andreas Tille <tille@debian.org>
# License: GPL
#
# UUD table carnivore_names contains sometimes more
# names for one and the same uploader.  To get identical
# names which are needed for some applications this tool
# helps to maintain a table
#    carnivore_name_prefered
# which contains the spelling of the name which should
# be prefered for such applications.

PORT=5441
DEFAULTPORT=5432
import psycopg2
from sys import stderr, exit
import re

debug=False
PREFEREDFACTOR=3
BLACKLIST = ('Thawte Freemail Member',
             'System V',
             'root',
             'Inc.',
             'q',
             'IV',
             'Boriel',
            )

WHITELIST = (
             'Abou Al Montacir',
             'Adam C. Powell IV',
             'Ahmed El-Said Atef El-Mahmoudy',
             'A Lee',
             'Alexander Pennace',
             'Alexander Reichle-Schmehl',
             'Alexandre Mestiashvili',
             'Ana Beatriz Guerrero López',
             'Andrew O. Shadoura',
             'Bastien Roucariès',
             'Bert Agaz',
             'Björn Andersson',
             'Björn Brenander',
             'Bob Hilliard',
             'Bruno Kleinert',
             'Chao-Ming',
             'Christian M. Amsüss',
             'Christine Caulfield',
             'Cleto Martin Angelina',
             'Dale E. Martin',
             'Daniel Nurmi',
             'Debian Calendarserver Team',
             'Debian Crosswire Packaging Team',
             'Debian Flash Team',
             'Debian FreeSmartphone.Org Team',
             'Debian Libidn Team',
             'Debian Med Packaging Team',
             'Debian PHP PEAR Maintainers',
             'Debian Printing Group',
             'Debian running development group',
             'Debian Science Team',
             'Debian TeX Maintainers',
             'Denis Rojo',
             'Erdal Ronahî',
             'Esteban Manchado Velázquez',
             'Eugeniy Meshcheryakov',
             'Fabio Massimo Di Nitto',
             'FAUmachine Team',
             'Francisco Manuel Garcia Claramonte',
             'Francois D. Menard',
             'Frederik Schüler',
             'Giuliano P Procida',
             'GOsa packages maintainers group',
             'Guido Günther',
             'Günter Milde',
             'Hubert Chan',
             'intrigeri',
             'Jameson Graef Rollins',
             'Jan Lübbe',
             'Javier Fernández-Sanguino Peña',
             'Jeremy Lainé',
             'Jérôme Marant',
             'Joel Aelwyn',
             'John Francesco Ferlito',
             'Joseph Nahmias',
             'Juan Rafael Alvarez Correa',
             'Kan-Ru Chen',
             'Krzysztof Krzyżaniak',
             'Loïc Minier',
             'Magosányi Árpád',
             'Maia Kozheva',
             'Martin Sjögren',
             'Michael Fladischer',
             'Michel Dänzer',
             'Mikael Sennerholm',
             'Morten Werner Forsbring',
             'Nicholas Flintham',
             'Nicolas François',
             'Niklas Höglund',
             'Noèl Köthe',
             'Paolo Didonè',
             'Philip Blundell',
             'Picca Frédéric-Emmanuel',
             'Radovan Garabík',
             'Ramakrishnan Muthukrishnan',
             'Raphaël Pinson',
             'Recai Oktaş',
             'Rémi Vanicat',
             'Sam Couter',
             'Santiago Ruano Rincón',
             'Scott M. Dier',
             'Simon Horman',
             'Stefan Völkel',
             'Stéphane Glondu',
             'Stephan Sürken',
             'Steve M. Robbins',
             'Tcl/Tk Debian Packagers',
             'Thomas Bushnell',
             'Tobias Quathamer',
             'Tony Palma',
             'Vanessa Gutiérrez',
             'W. Martin Borgert',
            )

has_quotes_re = re.compile('".*"')
has_second_initial_re = re.compile('^\w+ [A-Z]\. \w+$')

def prompt(prompt):
    return raw_input(prompt).strip()

def quote(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "''").replace('"', '""') + "'"

def List2PgArray(list):
    # turn a list of strings into the syntax for a PostgreSQL array:
    # {"string1","string2",...,"stringN"}
    if not list:
        return '{}'
    komma='{'
    PgArray=''
    for s in list:
        PgArray=PgArray+komma+'"'+ s.replace("'", "''").replace('"', '\\"') +'"'
        komma=','
    return PgArray+'}'

def StringWithoutQuotes(s):
    if has_quotes_re.match(s):
        if debug:
            print >>stderr, "Remove quotes from %s" % (s)
        return re.sub('"(.*)"', '\\1', s)
    return s

try:
    conn = psycopg2.connect(database="udd")
except psycopg2.OperationalError:
    try:
	conn = psycopg2.connect(port=PORT,database="udd")
	#conn = psycopg2.connect(port=PORT,user="tille",database="udd")
    except psycopg2.OperationalError:
        print >>stderr, "Problem connecting to UDD"
	exit(-1)
try:
    conn = psycopg2.connect(database="udd")
except psycopg2.OperationalError:
    try:
	conn = psycopg2.connect(port=PORT,database="udd")
    except psycopg2.OperationalError:
        print >>stderr, "Problem connecting to UDD"
	exit(-1)
curs = conn.cursor()

## Initialise carnivore_names_prefered table
query = """
DROP TABLE IF EXISTS carnivore_names_prefered;
CREATE TABLE carnivore_names_prefered (
  id   int,
  name text,
 PRIMARY KEY (id),
 FOREIGN KEY (id, name) REFERENCES carnivore_names DEFERRABLE);
GRANT SELECT ON carnivore_names_prefered TO PUBLIC;

-- Insert those names which are unique
INSERT INTO carnivore_names_prefered
   SELECT * FROM carnivore_names
       WHERE id in (SELECT id FROM carnivore_names
                 GROUP BY id HAVING COUNT(*) = 1);
"""
curs.execute(query)

# Check what name is used how often
query = """PREPARE name_usage (text[]) AS
        SELECT name, count(*) FROM (
            SELECT maintainer_name AS name FROM all_sources    WHERE maintainer_name = ANY($1)
            UNION ALL
            SELECT submitter_name  AS name FROM all_bugs       WHERE submitter_name  = ANY($1)
            UNION ALL
            SELECT owner_name      AS name FROM all_bugs       WHERE owner_name      = ANY($1)
            UNION ALL
            SELECT done_name       AS name FROM all_bugs       WHERE done_name       = ANY($1)
            UNION ALL
            SELECT name            AS name FROM uploaders      WHERE name            = ANY($1)
            UNION ALL
            SELECT changed_by_name AS name FROM upload_history WHERE changed_by_name = ANY($1)
            UNION ALL
            SELECT maintainer_name AS name FROM upload_history WHERE maintainer_name = ANY($1)
            UNION ALL
            SELECT signed_by_name  AS name FROM upload_history WHERE signed_by_name  = ANY($1)
        ) AS names
        GROUP BY name
        ORDER BY count DESC;"""
curs.execute(query)

query = "PREPARE insert_prefered_name AS INSERT INTO carnivore_names_prefered (id, name)  VALUES ($1, $2)"
curs.execute(query)

query = """SELECT name, id from carnivore_names cn
     WHERE id IN (SELECT id FROM carnivore_names
                  WHERE id not in (SELECT id FROM carnivore_names_prefered)
                 GROUP BY id HAVING COUNT(*) > 1)
   ORDER BY id;"""
curs.execute(query)

id=0
name = []
allnames = curs.fetchall()
for r in allnames:
    if id != r[1]:
        if id != 0:
            prefered = -1
            while prefered == -1:
                i=0
                query = "EXECUTE name_usage ('%s')" % List2PgArray(name)
                curs.execute(query)
                usednames = curs.fetchall()
                if len(usednames) == 0:
                    if debug:
                        print "Names %s are not used in sources at all" % str(name)
                    for n in name:
                        usednames.append((n,0))
                if len(usednames) == 1:
                    if debug:
                        print "Some names in carnivore_names of %s are not used in all_sources, all_bugs and uploaders" % str(name)
                    prefered = 0
                else:
                    if usednames[0][1] > PREFEREDFACTOR*usednames[1][1]:
                        if debug:
                            print "Name %s(%d) is way more prefered than %s(%d) and possibly others" % \
                                (usednames[0][0], usednames[0][1], usednames[1][0], usednames[1][1])
                        prefered = 0
                    else:
                        # Prefer upper cased names
                        if usednames[0][0].lower() == usednames[1][0].lower():
                            if usednames[0][0].istitle():
                                prefered = 0
                            else:
                               if usednames[1][0].istitle():
                                   prefered = 1
                            if debug:
                                print "Both name variants just have different capitalisation, %s is prefered." % usednames[prefered][0]
                        if len(usednames) == 2:
                            # prefer name versions with additional initial letter of second given name
                            if has_second_initial_re.match(usednames[0][0]):
                                if re.sub('^(\w+ )[A-Z]\. (\w+)$', '\\1\\2', usednames[0][0]) == usednames[1][0]:
                                    if debug:
                                        print "Most frequent name has second name initial %s" % usednames[0][0]
                                    prefered = 0
                            if has_second_initial_re.match(usednames[1][0]):
                                if re.sub('^(\w+ )[A-Z]\. (\w+)$', '\\1\\2', usednames[1][0]) == usednames[0][0]:
                                    if debug:
                                        print "Second frequent name has second name initial %s" % usednames[1][0]
                                    prefered = 1
                            if prefered < 0:
                                # check whether one name is a full part of the other name and choose the longer one as prefered name
                                if usednames[1][0].startswith(usednames[0][0]) or \
                                   usednames[1][0].endswith(usednames[0][0]):
                                    if debug:
                                        print "Second name '%s' completely contains first '%s' - use longer name" % \
                                            ( usednames[1][0], usednames[0][0])
                                    prefered = 1
                                if usednames[0][0].startswith(usednames[1][0]) or \
                                   usednames[0][0].endswith(usednames[1][0]):
                                    if debug:
                                        print "First name '%s' completely contains second '%s' - use longer name" % \
                                            ( usednames[0][0], usednames[1][0])
                                    prefered = 0
                        # check whitelist of names
                        i = -1
                        for u in usednames:
                            i += 1
                            if u[0] in WHITELIST:
                                prefered = i
                                if debug:
                                    print "Found %s in whitelist" % u[0]
                                break
                        if prefered < 0:
                            for n in usednames:
                                print "(%d)\t%s (%d)" % (i, n[0], n[1])
                                i += 1
                            s = prompt("Please type number of prefered name: ")
                            try:
                                si = int(s) - 1
                            except ValueError:
                                print "Please insert integer number"
                                continue
                            if si < 0 or si >= i:
                                print "Integer not in range"
                                continue
                            prefered = si
            try:
        	query = "EXECUTE insert_prefered_name (%d, %s)" % (id,  quote(usednames[prefered][0]))
    	    except IndexError, err:
    		print >>stderr, "Wrong index calculated: perfered = %i, (%s)" % (prefered, str(usednames)), err
    		conn.commit() # commit anyway previously injected changes
    		continue
            try:
                curs.execute(query)
            except psycopg2.ProgrammingError, err:
                print >>stderr, "%s: %s" % (err, query)
            conn.commit() # just commit after every insert to not see all names several times when checking this script
        id = r[1]
        name = []
        if r[0] not in BLACKLIST:
            name.append(StringWithoutQuotes(r[0]))
    else:
        if r[0] not in BLACKLIST:
            name.append(StringWithoutQuotes(r[0]))
