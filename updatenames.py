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
            'Ralf Gesellensetter':      {'project': 'edu', 'like': 'Ralf%setter'},
            'Vagrant Cascadian':        {'like': '%vagrant%'},
            'Francesco P. Lovergine':   {'like': 'Francesco%Lovergine', 'or': 'frankie'},
            'Christian Perrier':        {'author': ('bubulle', 'Christian PERRIER')},
            'Steve Langasek':           {'author': 'vorlon'},
            'Adrian von Bidder':        {'like': 'Adrian % von Bidder'},
            'Thomas Bushnell BSG':      {'like': 'Thomas Bushnell%BSG'},
            'Martin-Éric Racine':       {'like': 'Martin-%ric% Racine'},
            'Eddy Petrisor':            {'like': 'Eddy Petri%or'},
            'Linas Zvirblis':           {'like': 'Linas %virblis'},
            'Nicolas Évrard':           {'like': 'Nicolas %vrard'},
            'Piotr Ozarowski':          {'like': 'Piotr O%arowski'},
            'Charles Plessy':           {'like': 'charles-debian-nospam', 'or': 'plessy'},
            'Jean Luc COULON':          {'like': 'Jean-Luc Coulon%'},
            'Jérôme Warnier':           {'like': 'Jerome Warnier'},
            'Sven LUTHER':              {'project': 'ocaml-maint', 'author': 'Sven'},
            'Sven LUTHER':              {'author': 'Sven Luther'},
            'Steffen Möller':           {'author': ('smoe-guest', 'moeller', 'Steffen Moeller')},
            'Steven M. Robbins':        {'like': 'Steve%Robbins', 'or': 'smr'},
            'Charles Plessy':           {'author': ('plessy', 'charles-guest')},
            'David Paleino':            {'author': 'hanska-guest'},
            'Nelson A. de Oliveira':    {'author': 'naoliv'},
            'Andreas Tille':            {'author': ('tille', 'tillea', 'TilleA')},
            'Thijs Kinkhorst':          {'author': 'thijs'},
            'Mathieu Malaterre':        {'author': 'malat-guest'},
            'Morten Kjeldgaard':        {'author': 'mok0-guest'},
            'Tobias Quathamer':         {'author': 'Tobias Toedter'},
            'J.H.M. Dassen':            {'author': 'J.H.M.Dassen'},
            'L. V. Gandhi':             {'author': ('L . V . Gandhi', 'L.V.Gandhi')},
            'Jelmer Vernooij':          {'author': ('ctrlsoft-guest', 'jelmer')},
            'Mathieu Parent':           {'author': ('mparent-guest', 'Mathieu PARENT', 'sathieu')},
            'Noèl Köthe':               {'author': ('Noel Koethe', 'noel')},
            'Dominique Belhachemi':     {'author': 'domibel-guest'},
            'Philipp Benner':           {'author': 'pbenner-guest'},
            'Sylvestre Ledru':          {'author': ('sylvestre-guest', 'sylvestre', 'sylvestre.ledru')},
            'Christophe Prud_homme':    {'author': ('prudhomm', 'prudhomm-guest')},
            'Torsten Werner':           {'author': 'twerner'},
            'Jan Beyer':                {'author': ('beathovn-guest', 'jan\@beathovn.de')},
            'Filippo Rusconi':          {'author': ('Filippo Rusconi (Debian Maintainer)', 'rusconi')},
            'Daniel Leidert':           {'author': ('Daniel Leidert (dale)', 'dleidert-guest')},
            'Michael Banck':            {'author': 'mbanck'},
            'Guido Günther':            {'author': ('Guido G&#252;nther', 'Guido Guenther')},
            'Ahmed El-Mahmoudy':        {'like': '%Ahmed El-Mahmoudy%', 'or': 'aelmahmoudy-guest'},
            'Branden Robinson':         {'like': 'Branden Robinson%'},
            'LI Daobing':               {'author': 'lidaobing-guest'},
            'Nicholas Breen':           {'author': 'nbreen-guest'},
            'Egon Willighagen':         {'author': 'egonw-guest'},
            'Jordan Mantha':            {'author': 'laserjock-guest'},
            'Eric Sharkey':             {'author': 'sharkey'},
            'Fabio Tranchitella':       {'author': 'kobold'},
            'Petter Reinholdtsen':      {'author': 'pere'},
            'Andreas Putzo':            {'author': 'nd-guest'},
            'Giovanni Mascellani':      {'author': 'gmascellani-guest'},
            'Paul Wise':                {'author': ('pabs', 'pabs-guest')},
            'Alan Boudreault':          {'author': 'aboudreault-guest'},
            'Reinhard Tartler':         {'author': 'siretart'},
            'Alessio Treglia':          {'author': ('quadrispro-guest', 'alessio')},
            'M. Christophe Mutricy':    {'author': 'xtophe-guest'},
            'Jonas Smedegaard':         {'author': 'js'},
            'Jaromír Mikeš':            {'author': 'mira-guest'},
            'Adrian Knoth':             {'author': 'adiknoth-guest'},
            'Andres Mejia':             {'author': 'ceros-guest'},
            'Fabian Greffrath':         {'author': 'fabian-guest'},
            'Loïc Minier':              {'author': ('lool-guest', 'lool')},
            'Benjamin Drung':           {'author': 'bdrung-guest'},
            'Yaroslav Halchenko':       {'author': ('yoh-guest', 'yoh')},
            'Samuel Thibault':          {'author': ('sthibaul-guest', 'sthibault')},
            'Andrew Lee':               {'author': 'ajqlee'},
            'David Bremner':            {'author': 'bremner-guest'},
            'Christian Kastner':        {'author': 'chrisk'},
            'Christopher Walker':       {'author': 'cjw1006-guest'},
            'Michael Hanke':            {'author': 'mhanke-guest'},
            'Alastair McKinstry':       {'author': 'mckinstry'},
            'Otavio Salvador':          {'author': 'otavio'},
            'Frederic Lehobey':         {'author': ('fdl-guest', 'Frederic Daniel Luc Lehobey')},
            'Sylvain Le Gall':          {'author': 'Sylvain LE GALL'},
            'Hans-Christoph Steiner':   {'author': 'eighthave-guest'},
        }


def update_names(cur, conn):
    """Update the names with the items in NAMES."""
    for key, item in NAMES.iteritems():
        # 'like' and 'or'
        if 'like' in NAMES[key] and 'or' in NAMES[key]:
            try:
                curr.execute("""UPDATE listarchives
                            SET name = %s 
                            WHERE name LIKE %s
                            OR author = %s;""", (key, 
                                        NAMES[key]['like'], 
                                        NAMES[key]['or'])
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

            logging.info("Names matching 'like' and 'or' updated")
            continue

        # 'like'
        if 'like' in NAMES[key]:
            try:
                curr.execute("""UPDATE listarchives
                            SET name = %s
                            WHERE name LIKE %s;""", (key, NAMES[key]['like'])
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

            logging.info("Names matching 'like' updated")
            continue

        # 'author' or multiple authors
        if 'author' in NAMES[key]:
            author = NAMES[key]['author']
            if isinstance(author, basestring):
                try:
                    curr.execute("""UPDATE listarchives
                                SET name = %s
                                WHERE name = %s;""", (key, author)
                                )
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue
                logging.info('Author updated')
                continue
            else:
                query_lst = []
                author_lst = []
                for names in author:
                    author_lst.append(names)

                for number, element in enumerate(author_lst):
                    if number == 0:
                        query_lst.append("%s" % element)
                    else:
                        query_lst.append("OR name = %s" % element)
                query_string = " ".join(query_lst)
                try:
                    curr.execute("""UPDATE listarchives
                                SET name = %s
                                WHERE name = %s""", (key, query_string)
                                )
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue
                logging.info('Authors updated')
                continue
