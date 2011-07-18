#! /usr/bin/env python

"""Generates commit data statistics for SVN repositories.

This script generates SVN statistics for measuring team performance using
the metrics of: 

    - frequency of commits,
    - lines of code committed by a particular author.
"""

import os
import sys
import logging
import subprocess
import collections

from lxml import etree


def fetch_logs(ssh, conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""
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

            # Fetch the diff for each revision of an author.
            for change in revision:
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
                    print detail
                    continue

    logging.info('SVN logs saved...')
