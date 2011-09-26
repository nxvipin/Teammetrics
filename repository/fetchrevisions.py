#! /usr/bin/env python

import os
import shlex
import datetime
import subprocess
import collections

from xml.etree import ElementTree as ET

ALIOTH_PATH = '/srv/home/groups/teammetrics'
TEAM_FILE = os.path.join(ALIOTH_PATH, 'teams.list')
REVISION_FILE = os.path.join(ALIOTH_PATH, 'revisions.hash')
PARSE_INFO_FILE = os.path.join(ALIOTH_PATH, 'parse.info')

FORMAT = '{0},{1},{2},{3},{4},{5},{6},{7}'


def get_revisions():
    """Fetch the revisions that have already been saved."""
    revisions = []
    try:
        with open(REVISION_FILE) as f:
            revisions = [line.strip() for line in f.readlines()]
    except IOError: 
        revisions = []
    return revisions


def parse_revision():
    """Fetch the revisions for teams in TEAM_FILE."""
    revisions = collections.defaultdict(list)
    done_revisions = get_revisions()
    today_date = datetime.date.today()

    teams = []
    with open(TEAM_FILE) as f:
        teams = [line.strip() for line in f.readlines()]
    
    parse_f = open(PARSE_INFO_FILE, 'w')
    revision_f = open(REVISION_FILE, 'a')
    for team in teams:
        cmd_raw = 'svn log --xml file:///svn/{0}/'.format(team)
        cmd = shlex.split(cmd_raw)

        output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        output_xml = ET.fromstring(output)

        # Get the list of committers and their revisions from the repository.
        new_changes = []
        author_info = collections.defaultdict(list)
        revision_date = {}
        for info in output_xml.getiterator('logentry'):
            author, date, msg = [element.text for element in info.getchildren()]
            revision = int(info.get('revision'))
            author_info[author].append(revision)
            revision_date[revision] = date.split('T')[0]

        total_authors = len(author_info)
        for committer, revision in author_info.iteritems():
            project = team
            package = team
            author = committer

            # Fetch the diff for each revision of an author. If the revision
            # has already been downloaded, it won't be downloaded again.
            for change in revision:
                # Open the REVISION_FILE_PATH that is used to save the parsed revisions.
                inserted = 0
                deleted = 0

                change_format = '{0}:{1}'.format(project, change)
                if change_format in done_revisions:
                    continue

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

                parse_f.write(FORMAT.format(change, project, package, 
                                            author, revision_date[change],
                                            today_date, inserted, deleted))
                parse_f.write('\n')

                revision_f.write(change_format)
                revision_f.write('\n')

    parse_f.close()
    revision_f.close()

parse_revision()
