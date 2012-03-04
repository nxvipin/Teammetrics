#! /usr/bin/env python

import os
import sys
import shlex
import datetime
import subprocess
import collections

from xml.etree import ElementTree as ET

import checkrevision

ALIOTH_PATH = '/srv/home/groups/teammetrics'
PARSE_INFO_FILE = os.path.join(ALIOTH_PATH, 'parse.info')

IGNORE = ('unknown', 'None', 'root')
FORMAT = '{0},{1},{2},{3},{4},{5},{6}'
FORMAT_ALL = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'
SKIP_LINES = True


def parse_revision():
    """Fetch the revisions for the called teams."""
    revisions = collections.defaultdict(list)
    today_date = datetime.date.today()

    team = sys.argv[1]
    parse_f = open(PARSE_INFO_FILE, 'w')

    cmd_raw = 'svn log --xml file:///svn/{0}/'.format(team)
    cmd = shlex.split(cmd_raw)

    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    output_xml = ET.fromstring(output)

    # Get the list of committers and their revisions from the repository.
    new_changes = []
    author_info = collections.defaultdict(list)
    revision_date = {}
    for info in output_xml.getiterator('logentry'):
        # In some cases, the author tag is missing.
        try:
            author, date, msg = [element.text for element in info.getchildren()]
        except ValueError:
            continue
        revision = info.get('revision')
        author_info[author].append(revision)
        revision_date[revision] = date.split('T')[0]

    # Some authors are a result of missing authors or merges, so ignore them.
    for ignore_author in IGNORE:
        if ignore_author in author_info:
            del author_info[ignore_author]

    vcs = 'svn'
    total_authors = len(author_info)
    for committer, revision in author_info.iteritems():
        project = team
        package = team
        author = committer

        # Fetch the diff for each revision of an author. If the revision
        # has already been downloaded, it won't be downloaded again.
        done_revisions = checkrevision.read_configuration(team, 'svn')

        for change in revision:
            # Open the REVISION_FILE_PATH that is used to save the parsed revisions.
            if team in done_revisions:
                if change in done_revisions[team]:
                    continue

            if SKIP_LINES:
                parse_f.write(FORMAT.format(change, project, package, vcs,
                                            author, revision_date[change], today_date))
                parse_f.write('\n')
                parse_f.flush()
                checkrevision.save_configuration(project, change, 'svn')

            else:
                inserted = 0
                deleted = 0

                cmd_raw = 'svn diff -c {0} file:///svn/{1}/'.format(change, team)
                cmd = shlex.split(cmd_raw)
                output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

                lines = [line for line in output.splitlines()
                                                        if line.startswith(('+', '-'))]
                for line in lines:
                    if not line.startswith(('+++', '---')):
                        if line.startswith('+'):
                            inserted += 1
                        else:
                            deleted += 1

                parse_f.write(FORMAT_ALL.format(change, project, package, vcs,
                                                author, revision_date[change],
                                                today_date, inserted, deleted))
                parse_f.write('\n')
                parse_f.flush()
                checkrevision.save_configuration(project, change, 'svn')

    parse_f.close()
    sys.exit()

parse_revision()
