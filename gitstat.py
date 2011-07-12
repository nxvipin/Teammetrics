#! /usr/bin/env python

"""Generates commit data statistics for Git repositories.

This script will SSH into the Git repositories on Alioth and generate commmit
statistics for measuring team performance using the metrics of:

    - frequency of the commits,
    - the number of lines changed by a particular author.
"""

import os
import sys
import socket
import ConfigParser
import subprocess

import paramiko
import psycopg2

import updatenames

SERVER = 'vasks.debian.org'
USER = ''
PASSWORD = ''

CONF_FILE = 'commitinfo.conf'
CONF_FILE_PATH = os.path.join('/etc/teammetrics', CONF_FILE)
    

def get_configuration():
    """Read configuration data of repositories whose logs have to be fetched."""

    config = ConfigParser.SafeConfigParser()
    config.read(CONF_FILE_PATH)
    # Get the names for the mailing lists from the config file.
    sections = config.sections()

    # Create a mapping of the list name to the address(es).
    team_names = {}
    for section in sections:
        teams = []
        # In case the url and lists options are not found, skip the section.
        try:
            team = config.get(section, 'team').splitlines()
        except ConfigParser.NoOptionError as detail:
            logging.error(detail)
            continue
        if not team:
            logging.error('Team option cannot be empty in %s' % section)
            continue

        # Mapping of list-name to list URL (or a list of list-URLs).
        teams.append(team)
        # Flatten the list. 
        teams = sum(teams, [])
        team_names[section] = teams
    
    return team_names


def fetch_logs(ssh):
    # Get all authors in the repository.
    teams = []

    team_conf = get_configuration()
    for name, team_name in team_conf.iteritems():
        for each_team in team_name:
            teams.append(each_team)

    # Connect to the database and clear the table.
    conn = psycopg2.connect(database='teammetrics')
    cur = conn.cursor()
    cur.execute("""DELETE FROM gitstat;""");
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

                cur.execute(
                """INSERT INTO gitstat(project, package, name, 
                    changes, lines_inserted, lines_deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s);""",
                  (team, each_dir, author, changes, insert, delete)
                            )
                conn.commit()

    # Update the names.
    updatenames.update_names(cur, conn, table='gitstat')

    cur.close()
    conn.close()
    ssh.close()

    sys.exit('Quit')


def ssh_initialize():
    """Connect to the server specified using SSH."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    private_key_file = os.path.expanduser('~/.ssh/id_rsa')
    if not os.path.isfile(private_key_file):
        print 'SSH private key not found'
        sys.exit()
    
    try:
        user_key = paramiko.RSAKey.from_private_key_file(private_key_file,
                                                        password=PASSWORD)
    except (paramiko.PasswordRequiredException,
            paramiko.SSHException) as detail:
        print detail
        sys.exit()

    try:
        ssh.connect(SERVER, username=USER, pkey=user_key)
    except (paramiko.SSHException, socket.error) as detail:
        print detail
        sys.exit()

    fetch_logs(ssh)


if __name__ == '__main__':
    if not os.path.isfile(CONF_FILE_PATH):
        sys.exit('Configuration file not found')

    ssh_initialize()
