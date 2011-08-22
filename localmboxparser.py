#! /usr/bin/env python

import os
import sys
import logging

import liststat

LOG_FILE = 'localmbox.log'


def main(lst_files):
    for files in lst_files:
        project = os.path.basename(files).split('-')[0]
        lst_url = 'http://lists.debian.org/{0}'.format(project)
        liststat.parse_and_save({lst_url: files}, nntp=True)


def start_logging():
    """Initialize the logging."""
    logging.basicConfig(filename=LOG_FILE,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {0} <mbox-archives>'.format(sys.argv[0]))
    mbox_f = sys.argv[1:]

    start_logging()
    for files in mbox_f[:]:
        if not os.path.isfile(files):
            logging.error('Not a valid file: %s' % files)
            mbox_f.remove(files)

    main(mbox_f)
