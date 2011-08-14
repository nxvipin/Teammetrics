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

import psycopg2

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
                    revisions[row[0]] = row[1] 
            except (csv.Error, IndexError) as detail:
                logging.error(detail)
                sys.exit()
    except IOError: 
        revisions = {}

    return revisions


def save_revisions(revisions):
    """Save the revisions to REVISION_FILE."""
    with open(REVISION_FILE_PATH, 'w') as f:
        writer = csv.writer(f, delimiter=':')
        writer.writerows(revisions.iteritems())

    logging.info('Done writing revisions')


def fetch_logs(ssh, conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""
    revisions = collections.defaultdict(list)
    done_revisions = get_revisions()
    for team in teams:
        logging.info('Fetching team: %s' % team)
        cmd = 'svn log --xml file:///svn/{0}/'.format(team)

        stdin, stdout, stderr = ssh.exec_command(cmd)
        output_xml = etree.fromstring(stdout.read())

        # Get the list of committers and their revisions from the repository.
        new_changes = []
        author_info = collections.defaultdict(list)
        for info in output_xml.iter('logentry'):
            author = [author.text for author in info.iterchildren(tag='author')]
            revision = info.get('revision')
            author_info[''.join(author)].append(int(revision))

        total_authors = len(author_info)
        logging.info('There are %d authors' % total_authors)
        for committer, revision in author_info.iteritems():
            project = team
            package = team
            author = committer
            changes = len(author_info[committer])

            # Fetch the diff for each revision of an author. If the revision
            # has already been downloaded, it won't be downloaded again.
            inserted = 0
            deleted = 0
            old_changes = []

            if team in done_revisions:
                old_changes = done_revisions[team]

            for change in revision:
                if str(change) in old_changes:
                    logging.info('Skipping already done archive: %d' % change)
                    continue

                cmd = 'svn diff -c {0} file:///svn/{1}/'.format(change, team) 
                stdin, stdout, stderr = ssh.exec_command(cmd)

                output = stdout.read()
                lines = [line for line in output.splitlines() 
                                                        if line.startswith('+') 
                                                        or line.startswith('-')]

                for line in lines:
                    if line.startswith('+++') or line.startswith('---'):
                        continue
                    else: 
                        if line.startswith('+'):
                            inserted += 1
                        else:
                            deleted += 1

                logging.info('Parsed %d' % change)
                new_changes.append(change)

            # Save the information gathered to the database.
            try:
                cur.execute(
                """INSERT INTO commitstat(commit_id, project, package, vcs, name, 
                    changes, lines_inserted, lines_deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                  (revision, project, package, 'svn', author, changes, inserted, deleted)
                            )
                conn.commit()
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

        # Club all the revisions.
        all_revisions = list(itertools.chain(*author_info.values()))
        # Write the revisions corresponding to a team.
        total_changes = list(set(all_revisions) | set(new_changes))
        revisions[team] = total_changes

    save_revisions(revisions)
    logging.info('SVN logs saved...')
