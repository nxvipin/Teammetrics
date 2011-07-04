#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance (NNTP).

This script uses NNTP to fetch and parse the mailing lists on lists.debian.org via
the Gmane NNTP server (news.gmane.org). The metrics used for measuring team 
performance are the same as mentioned in the list parser for the lists on Alioth.
"""

import os
import time
import email
import socket
import urllib2
import logging
import nntplib
import datetime

import BeautifulSoup

import liststat

NNTP_SERVER = 'news.gmane.org'
NNTP_LIST = 'http://list.gmane.org'


def asctime_update(mail_asctime):
    """Returns a timestamp formatted to asctime and with the timezone adjusted.
    
    example:
        asctime_tz('Sat 4, Jun 2011 17:36:40 +0530')

    will return:
        Sat Jun  4 12:06:40 2011
    """

    # Parse date according to RFC 2822 but with the timezone info. 
    parse_date = email.utils.parsedate_tz(mail_asctime)
    # Get the timezone offset in seconds.
    tz_offset = parse_date[-1]
    # Create a timedelta with the timezone offset.
    tz = datetime.timedelta(seconds=tz_offset)
     
    asctime = datetime.datetime(*parse_date[:7], tzinfo=None)
    # The adjusted timezone according to the offset.
    asctime_updated = asctime - tz

    # Return an asctime string.
    return time.asctime(asctime_updated.timetuple())


def format_mail_name(from_field):
    """Returns a formatted version of the 'From' field.

    example:
        format_email_name('John Doe <john@doe.com>')
    
    will return:
        john at doe.com (John Doe)
    """

    # Get the email address.
    email_start_pos = from_field.find("<")
    email_end_pos = from_field.find(">")
    email_raw = from_field[email_start_pos+1:email_end_pos]
    email = email_raw.replace('@', ' at ')

    # Get the name. 
    name = from_field[:email_start_pos-1].strip()

    return email, name


def nntp_to_mbox(frm, date, sub, msg, body):
    """Convert the information fetched from the NNTP server to a mbox archive."""

    mbox_format = """From {0}
From: {1}
Date: {2}
Subject: {3}
Message-ID: {4}
"""
    with open('mbox_file', 'w') as mbox_file:
        for f, d, s, m, b in zip(frm, date, sub, msg, body):

            email, name = format_mail_name(f)
            updated_date = asctime_update(d)
            f_one = '{0}  {1}'.format(email, updated_date)
            f_two = '{0} ({1})'.format(email, name)
            
            mbox_file.write(mbox_format.format(f_one, f_two, d, s, m)) 
            mbox_file.write(b)


def main():
    # Get the configuration data from liststat.CONF_FILE_PATH.
    conf_info, total_lists = liststat.get_configuration(liststat.CONF_FILE_PATH, 
                                                                pipermail=False)
    counter = 0
    for names, lists in conf_info.iteritems():
        for lst in lists:                      
            logging.info('\tList %d of %d' % (counter+1, total_lists))

            # list-name@list-url redirects to the corresponding Gmane group.
            url, name = lst.rsplit('/', 1)
            # Strip the 'http://' from the URL.
            if url.startswith('http://'):
                url = url[len('http://'):]

            list_url = '{0}@{1}'.format(name, url)

            url_read = urllib2.urlopen('{0}/{1}'.format(NNTP_LIST, list_url))
            response = url_read.read()

            # Get the h1 tag because that holds the group name on Gmane.
            soup = BeautifulSoup.BeautifulSoup(response)
            heading = soup.h1.renderContents()
            if heading is None:
                logging.error('List %s not found' % list_url)
                continue
            group_name = heading.split()[-1]

            try:
                conn = nntplib.NNTP(NNTP_SERVER)
            except socket.error:
                logging.info('Unable to connect to the NNTP server')
                continue

            try:
                response, count, first, last, name = conn.group(group_name)
            except nntplib.NNTPTemporaryError as detail:
                logging.error(detail)
                counter += 1
                continue

            logging.info("Group '%s' has %s articles" % (name, count))

            from_lst = []
            date_lst = [] 
            subject_lst = []
            msg_id_lst = []

            msg_range = first + '-' + last
            resp, from_lst = conn.xhdr('From', msg_range)
            resp, subject_lst = conn.xhdr('Subject', msg_range)
            resp, date_lst = conn.xhdr('Date', msg_range)

            logging.info('Fetching headers for %s articles...' % count)

            body = []
            for i in range(int(first), int(last)+1):
                try:
                    resp, article_id, msg_id, msg = conn.body(str(i))
                    msg_id_lst.append(msg_id)
                    body.append('\n'.join(msg))
                except nntplib.NNTPTemporaryError as detail:
                    continue

            from_lst = [frm for (article_id, frm) in from_lst]
            date_lst = [date for (article_id, date) in date_lst]
            subject_lst = [subject for (article_id, subject) in subject_lst]

            nntp_to_mbox(from_lst, date_lst, subject_lst, msg_id_lst, body)

            counter += 1


if __name__ == '__main__':
    liststat.start_logging()
    logging.info('\t\tStarting NNTPListStat')

    main()
