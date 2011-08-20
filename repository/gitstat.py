#! /usr/bin/env python

"""Generates commit data statistics for Git repositories.

This script will SSH into the Git repositories on Alioth and generate commmit
statistics for measuring team performance using the metrics of:

    - frequency of the commits,
    - the number of lines changed by a particular author.

There is support for fetching statistics of multiple packages per team also.
"""

import os
import re
import sys
import socket
import logging
import datetime
import ConfigParser

import psycopg2

import updatenames


def fetch_logs(ssh, conn, cur, teams, users):
    """Fetch and save the logs for Git repositories by SSHing into Alioth."""

    today_date = datetime.date.today()
    # A regex pattern to match SHA-1 hashes.
    pattern = re.compile("[a-f0-9]{40}")

    for team in teams:
        # Connect to the database and clear the existing Git records because we
        # don't maintain a redundancy checker as fetching logs is fast; clear the
        # records only for the teams in the configuration file.
        logging.info('Clearing existing records of %s from database' % team)
        cur.execute("""DELETE FROM commitstat WHERE vcs='git' 
                                            AND project=%s;""", (team, ))
        conn.commit()

        # Get the directory listing.
        logging.info('Parsing repository: %s' % team)
        cwd = '/git/{0}'.format(team)

        stdin, stdout, stderr = ssh.exec_command("ls {0}".format(cwd))
        output = stdout.read()
        # Get only the git directories.
        git_dir = [dir for dir in output.splitlines() if dir.endswith('.git')]

        for each_dir in git_dir:
            no_debian = False
            logging.info('\tPackage: %s' % each_dir)
            cwd_process = cwd + '/{0}'.format(each_dir)
            
            # First fetch the authors who have committed to the Debian branch.
            # This is used to filter upstream contributors who are contributing
            # but are not part of the team and hence not part of the metrics.
            author_cmd = "git --git-dir={0} log --pretty=format:'%an' -- debian".format(cwd_process)
            stdin, stdout, stderr = ssh.exec_command(author_cmd)
            authors_lst = stdout.read().splitlines()

            # Uniquify the authors.
            authors = set(authors_lst)

            # But for teams who are not contributing to Debian development,
            # there is no Debian branch. So fetch all the statistics for them.
            if not authors:
                logging.warning('No Debian branch found')
                author_cmd = "git --git-dir={0} log --pretty=format:'%an'".format(cwd_process)
                stdin, stdout, stderr = ssh.exec_command(author_cmd)
                authors_lst = stdout.read().splitlines()
                authors = set(authors_lst)
                no_debian = True
                # If there are still no authors, go on to the next team. 
                if not authors:
                    continue

            # Fetch the commit details for each author.
            for author in authors:
                if no_debian:
                    stat_cmd = ("git --git-dir={0} log --no-merges --author='{1} <' "
                   "--pretty=format:'%H,%ai' --shortstat".format(cwd_process, author))
                else:
                    stat_cmd = ("git --git-dir={0} log --no-merges --author='{1} <' "
                   "--pretty=format:'%H,%ai' --shortstat -- debian".format(cwd_process, author))

                stdin, stdout, stderr = ssh.exec_command(stat_cmd)
                author_read = stdout.read().splitlines()

                # There are some log entries that don't have any lines changed
                # but are a commit of a merge or a tag. We filter entries.
                found = True
                for element in author_read[:]:
                    if pattern.match(element):
                        if not found:
                            element_index = author_read.index(element)
                            author_info.pop(element_index-1)
                        found = False
                    else:
                        found = True

                author_raw = [element.strip() for element in author_read 
                                                                    if element]

                author_info = []
                for a, b in zip(author_raw[::2], author_raw[1::2]):
                    author_info.append(a+','+b)

                for change in author_info:
                    try:
                        commit_hash, date_raw, changed, added, deleted = change.split(',')
                    except ValueError as detail:
                        logging.error(detail)
                        continue

                    # There are some invalid dates, just skip those commits.
                    try:
                        date = date_raw.split()[0]
                    except IndexError as detail:
                        logging.warning('Invalid date: %s' % date)
                        logging.error(detail)
                        continue
                    added = added.strip().split()[0]
                    deleted = deleted.strip().split()[0]

                    if each_dir.endswith('.git'):
                        each_dir = each_dir[:-4]

                    try:
                        cur.execute(
                        """INSERT INTO commitstat(commit_id, project, package, vcs, name, 
                            commit_date, today_date, lines_inserted, lines_deleted) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                  (commit_hash, team, each_dir, 'git', author, date, today_date, added, deleted)
                                    )
                        conn.commit()
                    except psycopg2.DataError as detail:
                        conn.rollback()
                        logging.error(detail)
                        continue

    logging.info('Git logs saved...')
