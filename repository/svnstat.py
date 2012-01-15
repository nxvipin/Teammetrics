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

    logging.info('Parsing repository data')
    ftp = ssh.open_sftp()
    ftp.chdir(ALIOTH_PATH)

    for team in teams:
        cmd = 'python {0}/fetchrevisions.py {1}'.format(ALIOTH_PATH, team)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read()

        logging.info('Fetching info from vasks.debian.org for %s...' % team)
        ftp.get('parse.info', 'parse.info')

        with open('parse.info') as f:
            try:
                cur.copy_from(f, 'commitstat', sep=',')
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
