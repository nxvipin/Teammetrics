#! /usr/bin/env python

"""Generates commit data statistics for SVN repositories.

This script generates SVN statistics for measuring team performance using
the metrics of: 

    - frequency of commits,
    - lines of code committed by a particular author.

All commands are executed locally on Alioth.
"""

import os
import sys
import csv
import logging
import datetime
import itertools
import subprocess
import collections

import psycopg2

from lxml import etree

REVISION_FILE = 'revisions.hash'
REVISION_FILE_PATH = os.path.join('/var/cache/teammetrics', REVISION_FILE)


def get_revisions():
    """Fetch the revisions that have already been saved."""
    revisions = []
    try:
        with open(REVISION_FILE_PATH) as f:
            revisions = [line.strip() for line in f.readlines()]
    except IOError: 
        revisions = []
    return revisions


def fetch_logs(ssh, conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""
    revisions = collections.defaultdict(list)
    done_revisions = get_revisions()
    today_date = datetime.date.today()


    for team in teams:
        logging.info('Fetching team: %s' % team)
        cmd = 'svn log --xml file:///svn/{0}/'.format(team)

        stdin, stdout, stderr = ssh.exec_command(cmd)
        output_xml = etree.fromstring(stdout.read())

        # Get the list of committers and their revisions from the repository.
        new_changes = []
        author_info = collections.defaultdict(list)
        revision_date = {}
        for info in output_xml.iter('logentry'):
            author = [author.text for author in info.iterchildren(tag='author')]
            revision = info.get('revision')
            author_info[''.join(author)].append(int(revision))
            revision_date[int(revision)] = ''.join([date.text.split('T')[0]
                                        for date in info.iterchildren(tag='date')])

        total_authors = len(author_info)
        logging.info('There are %d authors' % total_authors)
        for committer, revision in author_info.iteritems():
            project = team
            package = team
            author = committer

            # Fetch the diff for each revision of an author. If the revision
            # has already been downloaded, it won't be downloaded again.
            for change in revision:
                # Open the REVISION_FILE_PATH that is used to save the parsed revisions.
                f = open(REVISION_FILE_PATH, 'a')
                inserted = 0
                deleted = 0

                change_format = '{0}:{1}'.format(project, change)
                if change_format in done_revisions:
                    logging.info('Skipping already parsed revision: %d' % change)
                    continue

                cmd = 'svn diff -c {0} file:///svn/{1}/'.format(change, team) 
                stdin, stdout, stderr = ssh.exec_command(cmd)

                output = stdout.read()
                lines = [line for line in output.splitlines() if line.startswith(('+', '-'))]

                for line in lines:
                    if not line.startswith(('+++', '---')):
                        if line.startswith('+'):
                            inserted += 1
                        else:
                            deleted += 1

                # Save the information gathered to the database.
                try:
                    cur.execute(
                """INSERT INTO commitstat(commit_id, project, package, vcs, name, 
                    commit_date, today_date, lines_inserted, lines_deleted) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                            (change, project, package, 'svn', author, 
                    revision_date[change], today_date, inserted, deleted)
                                )
                    conn.commit()
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue
                except psycopg2.IntegrityError as detail:
                    conn.rollback()
                    logging.error('%s: project: %s, revision #: %d' % (detail, 
                                                                    project, 
                                                                    change))
                    continue

                logging.info('Parsed %d' % change)
                f.write(change_format)
                f.write('\n')
                f.close()

    logging.info('SVN logs saved...')
