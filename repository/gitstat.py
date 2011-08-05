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
import ConfigParser

import psycopg2

import updatenames


def fetch_logs(ssh, conn, cur, teams, users):
    """Fetch and save the logs for Git repositories by SSHing into Alioth."""

    # Connect to the database and clear the existing Git records because we
    # don't maintain a redundancy checker as fetching logs is fast.
    cur.execute("""DELETE FROM commitstat WHERE vcs='git';""");
    conn.commit()

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
                    logging.info('Upstream author %s' % author)
                    continue

                insertions = []
                deletions = []
                stat_cmd = ("git --git-dir={0} log --author='^{1}' "
                           "--pretty=format: --shortstat".format(cwd_process, author))
                
                stdin, stdout, stderr = ssh.exec_command(stat_cmd)
                author_info = stdout.read()

                author_info = [element.strip() for element in author_info.splitlines()
                                                                            if element]
                changes = len(author_info)
                for change in author_info:
                    changed, inserted, deleted = change.split(',')
                    insertions.append(int(inserted[1]))
                    deletions.append(int(deleted[1]))

                insert = sum(insertions)
                delete = sum(deletions)

                if each_dir.endswith('.git'):
                    each_dir = each_dir[:-4]

                try:
                    cur.execute(
                    """INSERT INTO commitstat(project, package, vcs, name, 
                        changes, lines_inserted, lines_deleted) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                      (team, each_dir, 'git', author, changes, insert, delete)
                                )
                    conn.commit()
                except psycopg2.DataError as detail:
                    conn.rollback()
                    print detail
                    continue

    logging.info('Git logs saved...')
