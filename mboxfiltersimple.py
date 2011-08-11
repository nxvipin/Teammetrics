#! /usr/bin/env python

import sys
import mailbox

HEADERS = ['From', 'Date', 'Subject', 'Message-ID', 'In-Reply-To', 'References']


def main(mbox_file):
    lines = []

    with open(mbox_file) as f:
        for line in f:
            lines.append(line)
    
    headers = []
    mbox = mailbox.mbox(mbox_file)
    for msg in mbox:
        headers.extend(msg.keys())

    whitelist = tuple(set(headers) - set(HEADERS)) 

    # Check each line whether it starts with the allowed header.
    for line in lines[:]:
        if line.startswith(whitelist):
            lines.remove(line)
    
    # Now save the file.
    with open(mbox_file, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Please provide the mbox file as an argument to the script')
    mbox_file = sys.argv[1]
    main(mbox_file)
