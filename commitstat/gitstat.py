#! /usr/bin/env python

"""Generates commit data statistics for Git repositories.

This script will SSH into the Git repositories on Alioth and generate commmit
statistics for measuring team performance using the metrics of:

    - frequency of the commits,
    - the number of lines changed by a particular author.
"""

import sys
import shlex
import subprocess

import psycopg2


def save_stats(author_stat):
    """Save the input mapping to a database."""
    conn = psycopg2.connect(database='teammetrics')
    cur = conn.cursor()

    # Delete the table before proceeding.
    cur.execute("""DELETE FROM gitstat;""");
    conn.commit()

    for name, commits in author_stat.iteritems(): 
        cur.execute(
    """INSERT INTO gitstat(project, name, changes, lines_inserted, lines_deleted) 
            VALUES (%s, %s, %s, %s, %s);""",
           ('foo', name, 
            author_stat[name]['change'], 
            author_stat[name]['insert'], 
            author_stat[name]['delete'])
                    )
        conn.commit()

    cur.close()
    conn.close()

    sys.exit('That\'s cool')


def main():
    # Get all authors in the repository.
    cmd = "git log --pretty=format:'%an'"
    author_cmd = shlex.split(cmd)
    all_authors = subprocess.Popen(author_cmd, 
                                    stdout=subprocess.PIPE).communicate()[0]
    authors_lst = all_authors.splitlines()

    # Uniquify the authors.
    authors = set(authors_lst)

    # Fetch the commit details for each author.
    author_stat = {}
    for author in authors:
        insertions = []
        deletions = []
        cmd = "git log --author='^{0}' --pretty=format: --shortstat".format(author)
        stat_cmd = shlex.split(cmd)

        author_info = subprocess.Popen(stat_cmd, 
                                        stdout=subprocess.PIPE).communicate()[0]
        author_info = [element.strip() for element in author_info.splitlines()
                                                                    if element]
        changes = len(author_info)
        for change in author_info:
            changed, inserted, deleted = change.split(',')
            insertions.append(int(inserted[1]))
            deletions.append(int(deleted[1]))

        author_stat[author] = {'change': changes, 
                                'insert': sum(insertions), 
                                'delete': sum(deletions)}

    save_stats(author_stat)


if __name__ == '__main__':
    main()
