#! /usr/bin/env python

"""Generates commit data statistics for SVN repositories.

This script generates SVN statistics for measuring team performance using
the metrics of: 

    - frequency of commits,
    - lines of code committed by a particular author.
"""

import os
import sys
import csv
import logging
import itertools
import subprocess
import collections

from lxml import etree

REVISION_FILE = 'revisions.hash'
REVISION_FILE_PATH = os.path.join('/var/cache/teammetrics', REVISION_FILE)


def get_revisions():
    """Fetch the revisions that have already been saved."""
    revisions = {}
    try:
        with open(REVISION_FILE_PATH) as f:
            reader = csv.reader(f, delimiter=':')
            try:
                for row in reader:
                    change = row[1].split(',')
                    revisions[row[0]] = change
            except (csv.Error, IndexError) as detail:
                logging.error(detail)
                sys.exit()
    except IOError: 
        revisions = {}

    return revisions


def save_revisions(revisions):
    """Save the revisions to REVISION_FILE."""
    with open(REVISION_FILE_PATH, 'a') as f:
        writer = csv.writer(f, delimiter=':')
        writer.writerows(revisions.iteritems())

    logging.info('Done writing revisions')


def fetch_logs(ssh, conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""
    revisions = {}
    done_revisions = get_revisions()
    for team in teams:
        cmd = 'svn log --xml file:///svn/{0}/'.format(team)

        stdin, stdout, stderr = ssh.exec_command(cmd)
        output_xml = etree.fromstring(stdout.read())

        # Get the list of committers and their revisions from the repository.
        author_info = collections.defaultdict(list)
        for info in output_xml.iter('logentry'):
            author = [author.text for author in info.iterchildren(tag='author')]
            revision = info.get('revision')
            author_info[''.join(author)].append(int(revision))

        for committer, revision in author_info.iteritems():
            project = team
            package = team
            author = committer
            changes = len(author_info[committer])

            # Fetch the diff for each revision of an author. If the revision
            # has already been downloaded, it won't be downloaded again.
            for change in revision:
                if team in done_revisions:
                    if str(change) in done_revisions[team]:
                        logging.info('Skipping already done archive: %d' % change)
                        continue

                cmd = 'svn diff -c {0} file:///svn/{1}/'.format(change, team) 
                stdin, stdout, stderr = ssh.exec_command(cmd)

                output = stdout.read()
                lines = [line for line in output.splitlines() 
                                                        if line.startswith('+') 
                                                        or line.startswith('-')]
                inserted = 0
                deleted = 0
                for line in lines:
                    if line.startswith('+++') or line.startswith('---'):
                        continue
                    else: 
                        if line.startswith('+'):
                            inserted += 1
                        else:
                            deleted += 1

                # Save the information gathered to the database.
                try:
                    cur.execute(
                    """INSERT INTO commitstat(project, package, vcs, name, 
                        changes, lines_inserted, lines_deleted) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                      (project, package, 'svn', author, changes, inserted, deleted)
                                )
                    conn.commit()
                except psycopg2.DataError as detail:
                    conn.rollback()
                    logging.error(detail)
                    continue

        # Flatten all the revisions.
        all_revisions = list(itertools.chain(*author_info.values())) 
        revisions[team] = ','.join(str(item) for item in all_revisions)

    # Update the revisions.
    save_revisions(revisions)

    logging.info('SVN logs saved...')
