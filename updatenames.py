#! /usr/bin/env python

"""Update the database with a single name for active posters that have been posting under multiple names.

The posters and their multiple names are stored in a mapping of real name to the variation:

        UPDATE listarchives SET name='Name' WHERE name ILIKE $FOO
"""

import os
import codecs
import logging

import psycopg2

import liststat

PROJECT_DIR = '/etc/teammetrics/'
NAME_FILE = os.path.join(PROJECT_DIR, 'names.list')
BOT_FILE = os.path.join(PROJECT_DIR, 'bots.list')


def parse_names():
    """Read NAME_FILE and return a mapping of real-name: variations."""
    name_variation = {}
    with codecs.open(NAME_FILE, encoding='utf-8') as f:
        for line in f:
            name, variations = line.split(':')
            name_variation[name.strip()] = [element.strip() for element in variations.split(',')]

    return name_variation


def parse_bots():
    """Read BOT_FILE and return the list of robots."""
    bots = [line.strip() for line in open(BOT_FILE)]
    return bots


def update_names(conn, cur, table='listarchives'):
    """Update the names with the items in NAMES."""
    names = parse_names()
    for key, item in names.iteritems():
        query = """UPDATE {0}
                SET name = %s
                WHERE name ILIKE %s""".format(table)

        if len(item) > 1:
            for i in range(len(item)-1):
                query += " OR name ILIKE %s"
            item.insert(0, key)
            query += ';'
            cur.execute(query, item)
            conn.commit()

        else:
            query += ';'
            cur.execute(query, (key, ''.join(item)))
            conn.commit()

    # Remove the bots from the list.
    logging.info('Removing bots')
    bots = parse_bots()
    for name in bots:
        query = """DELETE FROM {0}
                WHERE name ILIKE %s;""".format(table)
        cur.execute(query, (name,))
        conn.commit()


if __name__ == '__main__':
    DATABASE = liststat.DATABASE
    # Connect to the database.
    try:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['defaultport'])
    except psycopg2.OperationalError:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['port'])
    cur = conn.cursor()

    # Update the 'listarchives' and 'commitstat' tables.
    update_names(conn, cur)
    update_names(conn, cur, 'commitstat')
