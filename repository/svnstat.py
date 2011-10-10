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
import logging
import subprocess
import collections

import psycopg2

ALIOTH_PATH = '/srv/home/groups/teammetrics'


def fetch_logs(ssh, conn, cur, teams):
    """Fetch and save the logs for SVN repositories."""

    with open('teams.list', 'w') as f:
        f.write('\n'.join(teams))

    # Create a SFTPClient object to transfer the team list and revisions.
    ftp = ssh.open_sftp()
    ftp.chdir(ALIOTH_PATH)
    ftp.put('teams.list', 'teams.list')

    logging.info('Parsing repository data')
    cmd = 'python {0}/fetchrevisions.py'.format(ALIOTH_PATH)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read()

    logging.info('Fetching parse info from vasks.debian.org ...')
    ftp.get('parse.info', 'parse.info')

    parse_info = []
    with open('parse.info') as f:
        for line in f:
            rev, project, package, author, rev_date, parse_date, inserted, deleted = line.split(',')
            try:
                cur.execute(
            """INSERT INTO commitstat(commit_id, project, package, vcs, name, 
                commit_date, today_date, lines_inserted, lines_deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        (rev, project, package, 'svn', author, 
                    rev_date, parse_date, inserted, deleted)
                            )
                conn.commit()
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue
            except psycopg2.IntegrityError as detail:
                conn.rollback()
                logging.error('%s: project: %s, revision #: %s' % (detail, 
                                                                project, 
                                                                rev))
                continue

    logging.info('SVN logs saved...')
