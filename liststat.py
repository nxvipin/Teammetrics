#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance.

This script parses the mbox archives of the mailing lists specified and 
contributes to gauging team performance by using the following metrics:

  - the most active contributors, which is calculated using the frequency
of a sender using the 'From' header.
"""

import os
import re
import sys
import gzip
import mailbox
import urllib2
import collections

from BeautifulSoup import BeautifulSoup

LIST_FILE = 'listinfo'
LIST_DIRECTORY = '.teammetrics'
HOME_DIRECTORY = os.path.expanduser('~')

DIRECTORY_PATH = os.path.join(HOME_DIRECTORY, LIST_DIRECTORY)
LIST_FILE_PATH = os.path.join(DIRECTORY_PATH, LIST_FILE)


def main(): 
    """Parse the mbox file and return the frequency of contributors."""
    # Open the file with the list information (specified by LIST_FILE)
    # and save the lists to be parsed. 
    list_info = []
    with open(LIST_FILE_PATH, 'r') as f:
        for line in f:
            list_info.append(line.strip())

    # Filter out blank lines or strings, just in case.
    list_info = [element for element in list_info if element]

    # Create a list with the lists appended to the base URL.
    base_url = list_info[0]
    lists_parse = [base_url+element for element in list_info[1:]]

    print "Base URL is '{0}'.".format(base_url)
    total_lists = len(lists_parse)
    if not total_lists:
        sys.exit('No mailing list to parse.')

    count = 0
    dates = []
    mbox_files = []
    mbox_archives = []
    # Open the Pipermail archives page for each list in lists_parse.
    while True:
        for mailing_list in lists_parse:
            print '\n[{0} of {1}]'.format(count+1, total_lists)
            print "Reading: {0}".format(mailing_list)
            try:
                url = urllib2.urlopen(mailing_list)
            except urllib2.URLError, e:
                print("Error: Unable to fetch mailing list archive"
                                                "\nReason: {0}".format(e))
                count += 1
                continue                
            response = url.read()

            # Find all the <a> tags ending in '.txt.gz'.
            soup = BeautifulSoup(response)
            parse_dates = soup.findAll('a', href=re.compile('\.txt\.gz$'))
            # Extract the months from the <a> tags. This is used to download the
            # mbox archive corresponding to the months the list was active.
            dates.extend([str(element.get('href')) for element in parse_dates])

            # Skip if there are no dates.
            if not dates:
                print 'No dates found. Skipping.'
                count += 1
                continue
            # Download the mbox archives and save them to DIRECTORY_PATH.
            print 'Downloading {0} mbox archives...'.format(len(dates))
            for date in dates:
                mbox_url = '{0}/{1}'.format(mailing_list, date)
                mbox_archive_name = '{0}-{1}'.format(mailing_list.split('/')[-1],
                                                                            date)
                path_to_archive = os.path.join(DIRECTORY_PATH, mbox_archive_name)
                # Open the mbox archive and save it to the local disk.
                mbox = urllib2.urlopen(mbox_url)
                with open(path_to_archive, 'wb') as f:
                    mbox_archives.append(path_to_archive)
                    f.write(mbox.read())

                # Extract the mbox file from the gzip archive.
                mbox_file_name = '{0}'.format(mbox_archive_name.rsplit('.', 1)[0])
                path_to_mbox = os.path.join(DIRECTORY_PATH, mbox_file_name)
                with open(path_to_mbox, 'w') as gzip_file:
                    temp_file = gzip.open(path_to_archive, 'rb')
                    archive_contents = temp_file.read()
                    mbox_files.append(path_to_mbox)
                    gzip_file.write(archive_contents)
            count += 1
        break

    # We don't need the mbox archives, so delete them.
    print 'Cleaning up...' 
    for archives in mbox_archives:
        os.remove(archives)

    # Open each local mbox archive and then parse it to get the 'From' header.
    from_header = []
    for files in mbox_files:
        mbox_ = mailbox.mbox(files)
        for message in mbox_:
            from_header.append(message['From'])
        f.close()

    # Use only the first element. 
    from_header = [element.split()[0] for element in from_header]

    # Count the frequency of each sender. 
    from_frequency = collections.defaultdict(int)
    for sender in from_header:
        from_frequency[sender] += 1

    # Output the result.
    print ''
    for sender, count in from_frequency.iteritems():
        print '{0} - {1}'.format(sender, count)

    sys.exit('Quit')


if __name__ == '__main__':
    file_error = """Create a file '{0}' in the directory above with the format:
- Base URL in the first line,
  (example: http://lists.alioth.debian.org/pipermail/)
- followed by the name of each mailing list in a newline.""".format(LIST_FILE)
    if not os.path.isdir(DIRECTORY_PATH):
        print "Creating directory '{0}'...".format(DIRECTORY_PATH)
        os.mkdir(DIRECTORY_PATH)
        sys.exit(file_error)
    if not os.path.isfile(LIST_FILE_PATH):
        print "'{0}' not found in '{1}.'".format(LIST_FILE, DIRECTORY_PATH)
        sys.exit(file_error)

    main()
