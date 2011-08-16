#! /usr/bin/env python

"""Generates commit data statistics for Git repositories.

This script will SSH into the Git repositories on Alioth and generate commmit
statistics for measuring team performance using the metrics of:

    - frequency of the commits,
    - the number of lines changed by a particular author.

There is support for fetching statistics of multiple packages per team also.
"""

import os
import sys
import socket
import logging
import datetime
import ConfigParser

import psycopg2

import updatenames


def fetch_logs(ssh, conn, cur, teams, users):
    """Fetch and save the logs for Git repositories by SSHing into Alioth."""

    # Connect to the database and clear the existing Git records because we
    # don't maintain a redundancy checker as fetching logs is fast.
    cur.execute("""DELETE FROM commitstat WHERE vcs='git';""");
    conn.commit()

    today_date = datetime.date.today()
    for team in teams:
        # Get the directory listing.
        cwd = '/git/{0}'.format(team)

        stdin, stdout, stderr = ssh.exec_command("ls {0}".format(cwd))
        output = stdout.read()
        # Get only the git directories.
        git_dir = [dir for dir in output.splitlines() if dir.endswith('.git')]

        for each_dir in git_dir:
            cwd_process = cwd + '/{0}'.format(each_dir)
            
            author_cmd = "git --git-dir={0} log --pretty=format:'%an'".format(cwd_process)
            stdin, stdout, stderr = ssh.exec_command(author_cmd)
            authors_lst = stdout.read().splitlines()

            # Uniquify the authors.
            authors = set(authors_lst)

            # Fetch the commit details for each author.
            for author in authors:
                # For upstream contributors, filter them from the team.
                if not author in users:
                    logging.info('Upstream author: %s' % author)
                    continue

                stat_cmd = ("git --git-dir={0} log --author='^{1}' "
                           "--pretty=format:'%H,%ai' --shortstat".format(cwd_process, author))

                stdin, stdout, stderr = ssh.exec_command(stat_cmd)
                author_info = stdout.read()

                author_raw = [element.strip() for element in author_info.splitlines()
                                                                            if element]

                author_info = []
                for a, b in zip(author_raw[::2], author_raw[1::2]):
                    author_info.append(a+','+b)

                for change in author_info:
                    try:
                        commit_hash, date_raw, changed, added, deleted = change.split(',')
                    except ValueError:
                        continue
        
                    if len(commit_hash) != 40:
                        continue

                    date = date_raw.split()[0]
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
                        print detail
                        continue

    logging.info('Git logs saved...')
