#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Update the database with a single name for active posters that have been
posting under multiple names.

The posters and their multiple names are stored in a mapping:

    1.  UPDATE listarchives SET author = 'Name' WHERE author LIKE <name-1> OR author = <name-2>
        Name    :   { like : <name-1>, or : <name-2> }
    2.  UPDATE listarchives SET author = 'Name' WHERE author LIKE <name>
        Name    :   { like : <name> }
    3.  UPDATE listarchives SET author = 'Name' WHERE author = <author-1> OR author = <author-n>
        Name    :   { author : (<author-1 ... author-n>) }
"""

import logging

import psycopg2

import liststat

NAMES = {
            'Adrian Knoth':             {'author': 'adiknoth-guest'},
            'Adrian von Bidder':        {'like': 'Adrian % von Bidder'},
            'Ahmed El-Mahmoudy':        {'like': '%Ahmed El-Mahmoudy%', 'or': 'aelmahmoudy-guest'},
            'Alan Boudreault':          {'author': 'aboudreault-guest'},
            'Alastair McKinstry':       {'author': 'mckinstry'},
            'Alessio Treglia':          {'author': ('quadrispro-guest', 'alessio')},
            'Alexandre Mestiashvili':   {'author': 'Alex Mestiashvili'},
            'Andreas Putzo':            {'author': 'nd-guest'},
            'Andreas Tille':            {'author': ('Andreas T', 'tille@debian.org', 'Tille, Andreas', 'Tille A', 'tille', 'tillea', 'TilleA', '"Tille, Andreas"')},
            'Andres Mejia':             {'author': 'ceros-guest'},
            'Andrew Lee':               {'author': 'ajqlee'},
            'Benjamin Drung':           {'author': 'bdrung-guest'},
            'Branden Robinson':         {'like': 'Branden Robinson%'},
            'Charles Plessy':           {'author': ('plessy', 'charles-guest', 'charles-debian-nospam')},
            'Christian Kastner':        {'author': 'chrisk'},
            'Christian Perrier':        {'author': ('bubulle', 'Christian PERRIER')},
            'Christophe Prud_homme':    {'author': ('prudhomm', 'prudhomm-guest')},
            'Christopher Walker':       {'author': 'cjw1006-guest'},
            'Daniel Leidert':           {'author': ('Daniel Leidert (dale)', 'dleidert-guest')},
            'David Bremner':            {'author': 'bremner-guest'},
            'David Paleino':            {'author': 'hanska-guest'},
            'Dominique Belhachemi':     {'author': 'domibel-guest'},
            'Eddy Petrisor':            {'like': 'Eddy Petri%or'},
            'Egon Willighagen':         {'author': 'egonw-guest'},
            'Eric Sharkey':             {'author': 'sharkey'},
            'Fabian Greffrath':         {'author': 'fabian-guest'},
            'Fabio Tranchitella':       {'author': 'kobold'},
            'Filippo Rusconi':          {'author': ('Filippo Rusconi (Debian Maintainer)', 'rusconi')},
            'Francesco P. Lovergine':   {'like': 'Francesco%Lovergine', 'or': 'frankie'},
            'Frederic Lehobey':         {'author': ('fdl-guest', 'Frederic Daniel Luc Lehobey')},
            'Georges Khaznadar':        {'author': 'georgesk'},
            'Giovanni Mascellani':      {'author': 'gmascellani-guest'},
            'Guido Günther':            {'author': ('Guido G&#252;nther', 'Guido Guenther')},
            'Hans-Christoph Steiner':   {'author': 'eighthave-guest'},
            'J.H.M. Dassen':            {'author': 'J.H.M.Dassen'},
            'Jan Beyer':                {'author': ('beathovn-guest', 'jan\@beathovn.de')},
            'Jaromír Mikeš':            {'author': 'mira-guest'},
            'Jean Luc COULON':          {'like': 'Jean-Luc Coulon%'},
            'Jelmer Vernooij':          {'author': ('ctrlsoft-guest', 'jelmer')},
            'Jonas Smedegaard':         {'author': 'js'},
            'Jordan Mantha':            {'author': 'laserjock-guest'},
            'Jérôme Warnier':           {'like': 'Jerome Warnier'},
            'Karol Langner':            {'author': 'klm-guest'},
            'L. V. Gandhi':             {'author': ('L . V . Gandhi', 'L.V.Gandhi')},
            'LI Daobing':               {'author': 'lidaobing-guest'},
            'Linas Zvirblis':           {'like': 'Linas %virblis'},
            'Loïc Minier':              {'author': ('lool-guest', 'lool')},
            'M. Christophe Mutricy':    {'author': 'xtophe-guest'},
            'Martin-Éric Racine':       {'like': 'Martin-%ric% Racine'},
            'Mathieu Malaterre':        {'author': ('malat-guest', '"Mathieu Malaterre"')},
            'Mathieu Parent':           {'author': ('mparent-guest', 'Mathieu PARENT', 'sathieu')},
            'Mechtilde Stehmann':       {'author': 'Mechtilde'},
            'Michael Banck':            {'author': 'mbanck'},
            'Michael Hanke':            {'author': 'mhanke-guest'},
            'Moriyoshi Koizumi':        {'author': 'moriyoshi-guest'},
            'Morten Kjeldgaard':        {'author': 'mok0-guest'},
            'Nelson A. de Oliveira':    {'author': 'naoliv'},
            'Nicholas Breen':           {'author': 'nbreen-guest'},
            'Nicolas Évrard':           {'like': 'Nicolas %vrard'},
            'Noèl Köthe':               {'author': ('Noel Koethe', 'noel')},
            'Olivier Sallou':           {'like': '%olivier sallou%', 'or': '%sallou-guest'},
            'Otavio Salvador':          {'author': 'otavio'},
            'Paul Wise':                {'author': ('pabs', 'pabs-guest')},
            'Petter Reinholdtsen':      {'author': 'pere'},
            'Philipp Benner':           {'author': 'pbenner-guest'},
            'Piotr Ozarowski':          {'like': 'Piotr O%arowski'},
            'Ralf Gesellensetter':      {'like': 'Ralf%setter'},
            'Reinhard Tartler':         {'author': 'siretart'},
            'Samuel Thibault':          {'author': ('sthibaul-guest', 'sthibault')},
            'Steffen Möller':           {'author': ('smoe-guest', 'moeller', 'Steffen Moeller')},
            'Steve Langasek':           {'author': 'vorlon'},
            'Steven M. Robbins':        {'like': 'Steve%Robbins', 'or': 'smr'},
            'Sukhbir Singh':            {'author': 'sukhbir'},
            'Sven LUTHER':              {'author': ('Sven Luther', 'sven')},
            'Sylvain Le Gall':          {'author': 'Sylvain LE GALL'},
            'Sylvestre Ledru':          {'author': ('sylvestre-guest', 'sylvestre', 'sylvestre.ledru')},
            'Thijs Kinkhorst':          {'author': 'thijs'},
            'Thomas Bushnell BSG':      {'like': 'Thomas Bushnell%BSG'},
            'Tobias Quathamer':         {'author': 'Tobias Toedter'},
            'Torsten Werner':           {'author': 'twerner'},
            'Vagrant Cascadian':        {'like': '%vagrant%'},
            'Yaroslav Halchenko':       {'author': ('yoh-guest', 'yoh')},
        }

BOTS = (
            'Archive Administrator',
            'Cron Daemon',
            'BugScan reporter',
            'bts-link-upstream',
            'Debian Archive Maintenance',
            'Debian BTS',
            'Debian External Health System',
            'Debian testing watch',
            'Debian Bug Tracking System',
            'Debian FTP Masters',
            'Debian Installer',
            'Debian Boot CVS Master',
            'Skolelinux archive Installer',
            'NM Front D',
            'Debian Wiki'
       )

# new-name: old-name.
PROJECTS = {
            'blends': 'custom'
           }


def update_names(conn, cur, table='listarchives'):
    """Update the names with the items in NAMES."""
    for key, item in NAMES.iteritems():
        # 'like' and 'or'
        if 'like' in NAMES[key] and 'or' in NAMES[key]:
            query = """UPDATE {0}
                       SET name = %s 
                       WHERE name ILIKE %s
                       OR name = %s;""".format(table) 
            cur.execute(query, (key, NAMES[key]['like'], NAMES[key]['or']))
            conn.commit()
            continue

        # 'like'
        if 'like' in NAMES[key]:
            query = """UPDATE {0}
                       SET name = %s
                       WHERE name ILIKE %s;""".format(table)
            cur.execute(query, (key, NAMES[key]['like']))
            conn.commit()
            continue

        # 'author' or multiple authors
        if 'author' in NAMES[key]:
            author = NAMES[key]['author']
            if isinstance(author, basestring):
                query = """UPDATE {0}
                           SET name = %s
                           WHERE name = %s;""".format(table)
                cur.execute(query, (key, author))
                conn.commit()
                continue
            else:
                author_lst = []
                for names in author:
                    author_lst.append(names)

                query = """UPDATE {0}
                        SET name = %s 
                        WHERE name = %s""".format(table)

                for i in range(len(author_lst)-1):
                    query += " OR name = %s"
                author_lst.insert(0, key)
                query += ';'

                cur.execute(query, author_lst)
                conn.commit()
                continue
    
    # Update the project names in format of old-name: new-name.
    for new_name, old_name in PROJECTS.iteritems():
        query = """UPDATE {0}
                   SET project = %s
                   WHERE project = %s;""".format(table)
        cur.execute(query, (new_name, old_name))                    
        conn.commit()
        continue

    # Remove the bots from the list.
    logging.info('Removing bots')
    for name in BOTS:
        query = """DELETE FROM {0}
                WHERE name = %s;""".format(table)
        cur.execute(query, (name, ))
        conn.commit()


if __name__ == '__main__':
    DATABASE = liststat.DATABASE
    # Connect to the database.
    try:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['defaultport'])
    except psycopg2.OperationalError:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['port'])
    cur = conn.cursor()
    update_names(conn, cur)
    update_names(conn, cur, 'commitstat')
