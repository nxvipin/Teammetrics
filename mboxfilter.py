#! /usr/bin/env python

import sys
import mailbox

HEADERS = ('From',
           'Date',
           'Subject',
           'Message-ID',
           'In-Reply-To',
           'References',
           'Content-Type',
           'MIME-Version',
           'Content-Transfer-Encoding',
           'X-Spam-Status',
           'X-Debian-PR-Package',
           'X-Debian-PR-Keywords',
          )


def main(mbox_file):

    out_mbox = mbox_file + '.converted'
    mbox = open(out_mbox, 'w')

    with open(mbox_file) as f:
        stop = False
        first_add = True
        for line in f:

            if line.startswith(HEADERS):
                stop = False
                first_add = True

                print >>mbox, line,

            if stop:
                if first_add:
                    print >>mbox
                    first_add = False

                print >>mbox, line,
            
            if line == '\n':
                stop = True
            


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
