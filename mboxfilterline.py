#! /usr/bin/env python

import sys
import mailbox

HEADERS = ('From', 'Date', 'Subject', 'Message-ID', 'In-Reply-To', 'References')


def main(mbox_file):

    out_mbox = mbox_file + '.converted'
    mbox = open(out_mbox, 'w')

    stop = False
    with open(mbox_file) as f:
        for line in f:
            if stop:
                line_strip = line.strip()
                print >>mbox, line_strip
            if not line.strip():
                stop = True
                continue
            if line.startswith(HEADERS):
                stop = False
                print >>mbox, line.strip()



if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
