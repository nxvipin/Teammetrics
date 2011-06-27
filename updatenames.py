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

NAMES = {
            'Adrian Knoth':             {'author': 'adiknoth-guest'},
            'Adrian von Bidder':        {'like': 'Adrian % von Bidder'},
            'Ahmed El-Mahmoudy':        {'like': '%Ahmed El-Mahmoudy%', 'or': 'aelmahmoudy-guest'},
            'Alan Boudreault':          {'author': 'aboudreault-guest'},
            'Alastair McKinstry':       {'author': 'mckinstry'},
            'Alessio Treglia':          {'author': ('quadrispro-guest', 'alessio')},
            'Alexandre Mestiashvili':   {'author': 'Alex Mestiashvili'},
            'Andreas Putzo':            {'author': 'nd-guest'},
            'Andreas Tille':            {'author': ('tille', 'tillea', 'TilleA')},
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
            'L. V. Gandhi':             {'author': ('L . V . Gandhi', 'L.V.Gandhi')},
            'LI Daobing':               {'author': 'lidaobing-guest'},
            'Linas Zvirblis':           {'like': 'Linas %virblis'},
            'Loïc Minier':              {'author': ('lool-guest', 'lool')},
            'M. Christophe Mutricy':    {'author': 'xtophe-guest'},
            'Martin-Éric Racine':       {'like': 'Martin-%ric% Racine'},
            'Mathieu Malaterre':        {'author': 'malat-guest'},
            'Mathieu Parent':           {'author': ('mparent-guest', 'Mathieu PARENT', 'sathieu')},
            'Michael Banck':            {'author': 'mbanck'},
            'Michael Hanke':            {'author': 'mhanke-guest'},
            'Moriyoshi Koizumi':        {'author': 'moriyoshi-guest'},
            'Morten Kjeldgaard':        {'author': 'mok0-guest'},
            'Nelson A. de Oliveira':    {'author': 'naoliv'},
            'Nicholas Breen':           {'author': 'nbreen-guest'},
            'Nicolas Évrard':           {'like': 'Nicolas %vrard'},
            'Noèl Köthe':               {'author': ('Noel Koethe', 'noel')},
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


def update_names(cur, conn):
    """Update the names with the items in NAMES."""
    for key, item in NAMES.iteritems():
        # 'like' and 'or'
        if 'like' in NAMES[key] and 'or' in NAMES[key]:
            try:
                cur.execute("""UPDATE listarchives
                            SET name = %s 
                            WHERE name LIKE %s
                            OR name = %s;""", (key, 
                                        NAMES[key]['like'], 
                                        NAMES[key]['or'])
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

            conn.commit()
            continue

        # 'like'
        if 'like' in NAMES[key]:
            try:
                cur.execute("""UPDATE listarchives
                            SET name = %s
                            WHERE name LIKE %s;""", (key, NAMES[key]['like'])
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

            conn.commit()
            continue

        # 'author' or multiple authors
        if 'author' in NAMES[key]:
            author = NAMES[key]['author']
            if isinstance(author, basestring):
                try:
                    cur.execute("""UPDATE listarchives
                                SET name = %s
                                WHERE name = %s;""", (key, author)
                                )
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue

                conn.commit()
                continue
            else:
                author_lst = []
                for names in author:
                    author_lst.append(names)

                query = """UPDATE listarchives 
                        SET name = %s 
                        WHERE name = %s""" 

                for i in range(len(author_lst)-1):
                    query += " OR name = %s"
                author_lst.insert(0, key)
                query += ';'

                try:
                    cur.execute(query, author_lst)
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue

                conn.commit()
                continue
