#! /usr/bin/env python

import sys
import mailbox

HEADERS = ('From', 'Date', 'Subject', 'Message-ID', 'In-Reply-To', 'References')


def main(mbox_file):

    out_mbox = mbox_file + '.converted'
    mbox = open(out_mbox, 'w')

    stop = False
    first_run = True
    first_add = True
    with open(mbox_file) as f:
        for line in f:

            if stop:
                if first_add:
                    print >>mbox
                    first_add = False

                print >>mbox, line,
                continue
            
            if line == '\n':
                first_run = False
                stop = True
                continue
            
            if line.startswith(HEADERS):
                stop = False
                first_add = True

                print >>mbox, line,
                continue


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
