#! /usr/bin/env python

import os
import sys
import mailbox

import nntpstat

HEADERS = ['From', 'Date', 'Subject', 'Message-ID', 'In-Reply-To', 'References']

def main(mbox_file):
    mbox = mailbox.mbox(mbox_file)

    content = []
    header  = []

    for message in mbox:
	tmpheader = {}
	for h in HEADERS:
	    tmpheader[h] = message[h]
	header.append(tmpheader)
        raw_content = message.get_payload()
        if isinstance(raw_content, list):
            content.append(raw_content[0].get_payload())
        else:
            content.append(raw_content)

    mbox.close()

    with open(mbox_file, 'w') as mbox_f:
        for h, c in zip(header, content):
            email, name = nntpstat.format_mail_name(h['From'])
            updated_date = nntpstat.asctime_update(h['Date'], h['Message-ID'])
            h['From0'] = '{0}  {1}'.format(email, updated_date)
            h['From']  = '{0} ({1})'.format(email, name)
          
	    mbox_format = "From %(From0)s\n"
	    for hx in HEADERS:
		if h.has_key(hx) and h[hx] != None:
		    mbox_format = mbox_format + hx + ": %(" + hx + ")s\n"
	    mbox_format = mbox_format + "\n"

            mbox_f.write(mbox_format % (h)) 
            try:
                mbox_f.writelines(c)
            except TypeError, err:
                print str(h['Message-ID']) + "\n" + str(err) + "\n" + str(c)

            mbox_f.write('\n')

    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
