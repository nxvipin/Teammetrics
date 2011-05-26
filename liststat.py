#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance.

This script parses the mbox archives of the mailing lists specified and 
contributes to gauging team performance by using the following metrics:

    - the most active contributors, which is calculated using the frequency
    of a sender using the 'From' header.
"""

import os
import sys
import mailbox
import collections

ALIOTH_URL = 'http://lists.alioth.debian.org/pipermail/'
MAILING_LISTS = (
                    'blends-commit',
                    'debian-med-commit',
                    'debian-med-packaging',
                    'debian-science-commits',
                    'debian-science-maintainers',
                    'debichem-commits',
                    'debichem-devel',
                    'debtags-devel',
                    'pkg-grass-devel',
                    'pkg-java-maintainers',
                    'pkg-multimedia-commits',
                    'pkg-multimedia-maintainers',
                    'pkg-samba-maint',
                    'pkg-scicomp-commits',
                    'pkg-scicomp-devel'
                )


def main(file_): 
    """Parse the mbox file and return the frequency of contributors."""
    mbox_file = mailbox.mbox(file_)
    
    # Get the 'From' header from the mbox.
    from_header = []
    for message in mbox_file:
        from_header.append(message['From'])

    # Use only the first element. 
    from_header = [element.split()[0] for element in from_header]

    # Count the frequency of each sender. 
    from_frequency = collections.defaultdict(int)
    for sender in from_header:
        from_frequency[sender] += 1

    # Output the result.
    for sender, count in from_frequency.iteritems():
        print '{0} - {1}'.format(sender, count)

    sys.exit('Quit')


if __name__ == '__main__':
    file_name = sys.argv[1]
    if not os.path.isfile(file_name):
        sys.exit("The file does not exist.")
    main(file_name)
