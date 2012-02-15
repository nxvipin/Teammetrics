#! /usr/bin/env python

import os
import ConfigParser

GIT_REVISION = os.path.join('/var/cache/teammetrics', 'revisions.hash')

ALIOTH_PATH = '/srv/home/groups/teammetrics'
SVN_REVISION = os.path.join(ALIOTH_PATH, 'revisions.hash')


def get_vcs(vcs):
    """Returns the path of the corresponding VCS."""
    if vcs == 'git':
        return GIT_REVISION
    if vcs == 'svn':
        return SVN_REVISION


def read_configuration(name, vcs):
    """Read the configuration file and fetch the revisions.

    This function is VCS specific because the SVN revisions are saved on
    vasks.debian.org while the Git revisions are on blends.debian.net.
    """

    config_file = get_vcs(vcs)
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_file)

    name_revisions = {}
    if parser.has_section(name):
        name_revisions[name] = [e.strip() for e in parser.get(name, 'revisions').split(',')]

    return name_revisions


def save_configuration(name, revisions, vcs):
    """Writes the configuration file with the revision information."""

    config_file = get_vcs(vcs)
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_file)

    if not parser.has_section(name):
        parser.add_section(name)

    try:
        parsed_revisions = parser.get(name, 'revisions')
        save_revision = '{0},{1}'.format(parsed_revisions, revisions)
    except ConfigParser.NoOptionError:
        save_revision = revisions

    parser.set(name, 'revisions', save_revision)
    parser.write(open(config_file, 'w'))
