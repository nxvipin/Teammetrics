#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance.

This script downloads mbox archives for the mailing list(s) specified, parses
them and generates statistical data about:

  * the most active contributors, which is calculated using the frequency of a
sender using the 'From' header.

This script works for any mailing list that runs on GNU Mailman and where 
Pipermail is used as the mail archiver. You just need to specify the list URL
and the script will automatically download all the mbox archives, parse them
and generate statistical data. The data generated is stored in a mapping, so 
it's easy to output it in the format you desire. 
  
"""

import os
import re
import sys
import gzip
import mailbox
import urllib2
import collections
import ConfigParser

from BeautifulSoup import BeautifulSoup

PROJECT_DIR = 'teammetrics'

CONF_FILE = 'listinfo.conf'
CONF_SAVE_DIR = '/etc'
CONF_PATH = os.path.join(CONF_SAVE_DIR, PROJECT_DIR) 
CONF_FILE_PATH = os.path.join(CONF_SAVE_DIR, PROJECT_DIR, CONF_FILE)

ARCHIVES_SAVE_DIR = '/var/cache'
ARCHIVES_FILE_PATH = os.path.join(ARCHIVES_SAVE_DIR, PROJECT_DIR)


def get_configuration():
    """Read the lists to be parsed from the configuration file."""
    config = ConfigParser.SafeConfigParser()
    try:
        config.read(CONF_FILE_PATH)
    except ConfigParser.Error as detail:
        print detail
    # Get the names for the mailing lists from the config file.
    sections = [section for section in config.sections()]

    # Create a mapping of the list name to the address(es).
    mailing_list_parse = {}
    for section in sections:
        mailing_list = []
        # In case the url and lists options are not found, skip the section.
        try:
            base_url = config.get(section, 'url')
            list_ = config.get(section, 'lists').splitlines()
        except ConfigParser.NoOptionError as detail:
            print detail
            continue
        if not base_url:
            print 'Base URL cannot be empty. Skipping', section
            continue
        if not list_:
            print 'List URL cannot be empty. Skipping', section
            continue
        # Just in case someone forgot to append the /.
        for each_list in list_:
            if base_url.endswith('/'):
                mailing_list.append('{0}{1}'.format(base_url, each_list))
            else:
                mailing_list.append('{0}/{1}'.format(base_url, each_list))
        # Mapping of list-name to list URL (or a list of list-URLs).
        mailing_list_parse[section] = mailing_list

    return mailing_list_parse


def is_root():
    """Check if the user has root privileges."""
    # If the user doesn't have root privileges, quit. We plan to fix this 
    # later by creating a teammetrics group but for now this is the only way.
    if os.getuid():
        sys.exit('Please run this script with root privileges.')


def main(conf_info): 
    """Parse the mbox file and return the frequency of contributors."""
    # Calculate the total number of lists by iterating through the values of 
    # conf_info. Note that there are multiple values per key. 
    total_lists = len([item for items in conf_info.values() for item in items])
    if not total_lists:
        sys.exit('Quit - no lists.')

    count = 0
    mbox_files = []
    mbox_archives = []
    # The conf_info has a mapping of {list-name : [list-url]}. So we go through
    # each value and download the corresponding list.
    for names, lists in conf_info.iteritems():
        for name in names:
            for list_ in lists:
                print '\n[{0} of {1}]'.format(count+1, total_lists)
                print "Reading: {0}".format(list_)
                try:
                    url = urllib2.urlopen(list_)
                except (urllib2.URLError, ValueError) as e:
                    print("Error: Unable to fetch mailing list archive"
                                                    "\nReason: {0}".format(e))
                    count += 1
                    continue                
                response = url.read()

                # Find all the <a> tags ending in '.txt.gz'.
                soup = BeautifulSoup(response)
                parse_dates = soup.findAll('a', href=re.compile('\.txt\.gz$'))
                # Extract the months from the <a> tags. This is used to download
                # the mbox archive corresponding to the months the list was active.
                dates = []
                dates.extend([str(element.get('href')) for element in parse_dates])

                # Skip if there are no dates.
                if not dates:
                    print 'No dates found. Skipping.'
                    count += 1
                    continue

                # Download the mbox archives and save them to DIRECTORY_PATH.
                print 'Downloading {0} mbox archives...'.format(len(dates))
                for date in dates:
                    mbox_url = '{0}/{1}'.format(list_, date)
                    mbox_archive_name = '{0}-{1}'.format(list_.split('/')[-1], date)
                    path_to_archive = os.path.join(ARCHIVES_FILE_PATH, 
                                                    mbox_archive_name)
                    # Open the mbox archive and save it to the local disk.
                    try:
                        mbox = urllib2.urlopen(mbox_url)
                    except urllib2.URLError, e:
                        print "Error: ", e, mbox_url
                        count += 1
                        continue
                    with open(path_to_archive, 'wb') as f:
                        mbox_archives.append(path_to_archive)
                        f.write(mbox.read())

                    # Extract the mbox file (plain text) from the gzip archive. 
                    mbox_file_name = '{0}'.format(mbox_archive_name.rsplit('.', 1)[0])
                    path_to_mbox = os.path.join(ARCHIVES_FILE_PATH, mbox_file_name)
                    with open(path_to_mbox, 'w') as gzip_file:
                        temp_file = gzip.open(path_to_archive, 'rb')
                        archive_contents = temp_file.read()
                        mbox_files.append(path_to_mbox)
                        gzip_file.write(archive_contents)
                count += 1
            break

    # We don't need the mbox archives, so delete them.
    if mbox_archives:
        print '\nCleaning up...' 
        for archives in mbox_archives:
            os.remove(archives)

    # Open each local mbox archive and then parse it to get the 'From' header.
    from_header = []
    for files in mbox_files:
        mbox_ = mailbox.mbox(files)
        for message in mbox_:
            from_header.append(message['From'])

    # Use only the first element (this will be changed later).  
    from_header = [element.split()[0] for element in from_header 
                                                    if element is not None]

    # Count the frequency of each sender. Note that this is a mapping of
    # address : frequency. So you can use this to output the data in any
    # format you desire by iterating over this.
    from_frequency = collections.defaultdict(int)
    for sender in from_header:
        from_frequency[sender] += 1

    # Output the result to the console for now.
    print ''
    print '-- Statistics --'
    for sender, count in from_frequency.iteritems():
        print '{0} - {1}'.format(sender, count)

    # The highest contributor. 
    max_contrib = max(from_frequency, key=from_frequency.get)
    print 'Maximum contributions by: ', max_contrib, from_frequency[max_contrib]

    sys.exit('\nQuit')


if __name__ == '__main__':
    is_root()
    conf_info = get_configuration()
    # Create the directories on first run. NOTE: This will be changed later. 
    if not os.path.isdir(ARCHIVES_FILE_PATH):
        os.mkdir(ARCHIVES_FILE_PATH)
        print 'Directory created', ARCHIVES_FILE_PATH
    if not os.path.isdir(CONF_PATH):
        os.mkdir(CONF_PATH)
        sys.exit('Directory created {0}'.format(CONF_PATH))
    if not os.path.isfile(CONF_FILE_PATH):
        sys.exit('File not found {0}'.format(CONF_FILE_PATH))
    main(conf_info)
