#! /usr/bin/env python

"""Generates commit data statistics for SVN repositories.

This script generates SVN statistics for measuring team performance using
the metrics of: 

    - frequency of commits,
    - lines of code committed by a particular author.
"""

import os
import sys
import shlex
import subprocess
import collections

from lxml import etree

SVN_REPO = 'svn://anonscm.debian.org'


def fetch_logs(conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""
    for team in teams:
        url = '{0}/{1}'.format(SVN_REPO, team)
        cmd = 'svn log --xml {0}'.format(url)
        log_cmd = shlex.split(cmd)

        output, error = subprocess.Popen(log_cmd, 
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE).communicate()
        if error:
            logging.error('An error has occurred %s' % error)
            continue

        output_xml = etree.fromstring(output)

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
                cmd = 'svn diff -c {0} {1}'.format(change, url) 
                rev_cmd = shlex.split(cmd)

                output, error = subprocess.Popen(rev_cmd, 
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE).communicate()
                
                if error:
                    logging.error('Error fetching diff for revision %d' % change)
                
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
