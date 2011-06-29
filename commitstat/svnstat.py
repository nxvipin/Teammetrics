#! /usr/bin/env python

"""Generates commmit data statistics for SVN repositories.

This script generates commit statistics for SVN repositories for measuring
team performance using the metrics of:
    
    - frequency of the commits.
"""

import sys
import shlex
import subprocess

from lxml import etree


def main():
    cmd = "svn log --xml {0}"
    svn_log = shlex.split(cmd)

    process = subprocess.Popen(svn_log, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        sys.exit("Invalid repository/ repository doesn't exist")

    element = etree.fromstring(output)
    authors = []
    for author in element.iter('author'):
        authors.append(author.text)

    print authors


if __name__ == '__main__':
    main()
