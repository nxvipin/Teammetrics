#! /usr/bin/env python

import os
import sys
import mailbox

import nntpstat


def main(mbox_file):
    mbox = mailbox.mbox(mbox_file)

    from_field = []
    date = []
    subject = []
    msg_id = []
    content = []

    for message in mbox:
        from_field.append(message['From'])
        date.append(message['Date'])
        subject.append(message['Subject'])
        msg_id.append(message['Message-Id'])
        raw_content = message.get_payload()
        if isinstance(raw_content, list):
            content.append(raw_content[0].get_payload())
        else:
            content.append(raw_content)

    mbox.close()

    mbox_format = """From {0}
From: {1}
Date: {2}
Subject: {3}
Message-ID: {4}
"""

    with open(mbox_file, 'w') as mbox_f:
        for f, d, s, m, c in zip(from_field, date, subject, msg_id, content):

            email, name = nntpstat.format_mail_name(f)
            updated_date = nntpstat.asctime_update(d, m)
            f_one = '{0}  {1}'.format(email, updated_date)
            f_two = '{0} ({1})'.format(email, name)
          
            mbox_f.write(mbox_format.format(f_one, f_two, d, s, m)) 
            try:
                mbox_f.writelines(c)
            except TypeError:
                pass

            mbox_f.write('\n')

    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <mbox>' % (sys.argv[0]))
    mbox_file = sys.argv[1]
    main(mbox_file)
