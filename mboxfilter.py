#! /usr/bin/env python

import sys
import mailbox

HEADERS = ('From',
           'Date',
           'Subject',
           'Message-ID',
           'Message-Id',
           'In-Reply-To',
           'References',
           'Content-Type',
           'MIME-Version',
           'Content-Transfer-Encoding',
           'X-Spam-Status',
           'X-Debian-PR-Package',
           'X-Debian-PR-Keywords',)

MULTI_HEADERS = ('Content-Type')


def main(mbox_file):

    out_mbox = mbox_file + '.converted'
    mbox = open(out_mbox, 'w')

    with open(mbox_file) as f:
        stop = False
        start_h = False
        first_add = True
        header = True

        for line in f:

            if start_h:
                if header:
                    if line.startswith((' ', '\t')):
                        print >>mbox, line, 

            if line.startswith(HEADERS):
                if header:
                    start_h = False

                    if line.startswith(MULTI_HEADERS):
                        start_h = True

                    stop = False
                    first_add = True

                    print >>mbox, line,

            if stop:
                header = False
                if first_add:
                    print >>mbox
                    first_add = False

                print >>mbox, line,
            
            if line == '\n':
                stop = True
                header = True
                start_h = False
            
    print 'Headers stripped from mbox'

    # Now open the converted mbox archive to delete messages with the
    # Message-IDs specified in the file messageid.
    msg_ids = []
    try:
        with open('messageid') as f:
            msg_ids = [line.strip() for line in f.readlines()]
    except IOError:
        sys.exit('Error: messageid file not found in current working directory')

    mbox = mailbox.mbox(out_mbox)

    mbox.lock()
    counter = 0

    for key, msg in mbox.iteritems():
        msg_id = msg['Message-ID']
        if msg_id in msg_ids: 
            mbox.remove(key)
            counter += 1

    print 'Deleted %d messages' % counter

    mbox.flush()
    mbox.close()
    sys.exit('Done')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
