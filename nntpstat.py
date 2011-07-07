#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance (NNTP).

This script uses NNTP to fetch and parse the mailing lists on lists.debian.org via
the Gmane NNTP server (news.gmane.org). The metrics used for measuring team 
performance are the same as mentioned in the list parser for the lists on Alioth.
"""

import os
import csv
import sys
import time
import email
import socket
import urllib2
import logging
import nntplib
import datetime
import ConfigParser

import BeautifulSoup

import liststat

NNTP_CONF_FILE = 'nntplists.hash'
NNTP_CONF_SAVE_PATH = os.path.join(liststat.ARCHIVES_SAVE_DIR, 
                                      liststat.PROJECT_DIR,
                                      NNTP_CONF_FILE)

NNTP_SERVER = 'news.gmane.org'
NNTP_LIST = 'http://list.gmane.org'


def get_parsed_lists():
    """Read the configuration data of lists that have been parsed.
    
    This is used to prevent redundancy by preventing downloading of articles
    that have already been fetched and parsed from the server. 
    """

    config = ConfigParser.SafeConfigParser()
    config.read(NNTP_CONF_SAVE_PATH)
    # Get the names for the mailing lists from the config file.
    sections = config.sections()

    # Create a mapping of the list name to the address(es).
    nntp_list_parse = {}
    for section in sections:
        # In case the url and lists options are not found, skip the section.
        try:
            end = config.get(section, 'end')
        except ConfigParser.NoOptionError as detail:
            logging.error(detail)
            continue
        if not end:
            logging.error('End option cannot be empty in %s' % section)
            continue

        # Mapping of list-name to list URL (or a list of list-URLs).
        nntp_list_parse[section] = {'end': end}

    return nntp_list_parse


def save_parsed_lists(lst, end):
    """Save the configuration data of lists that have been parsed."""
    config = ConfigParser.SafeConfigParser()
    config.read(NNTP_CONF_SAVE_PATH)

    # Clear the previous configuration for the particular list.
    if lst in config.sections():
        config.remove_section(lst)

    # Now add the new pot
    config.add_section(lst)
    config.set(lst, 'end', str(end))
    with open(NNTP_CONF_SAVE_PATH, 'w') as f:
        config.write(f)

    logging.info('Configuration settings updated')


def today_date():
    """Returns the current date formatted to 'date-month-year'."""
    date_now = datetime.datetime.now()
    return date_now.strftime('%d-%b-%Y')


def asctime_update(mail_asctime):
    """Returns a timestamp formatted to asctime and with the timezone adjusted.
    
    example:
        asctime_tz('Sat 4, Jun 2011 17:36:40 +0530')

    will return:
        Sat Jun  4 12:06:40 2011
    """

    # Parse date according to RFC 2822 but with the timezone info. 
    parse_date = email.utils.parsedate_tz(mail_asctime)
    # Get the timezone offset in seconds and create a timezone delta.
    tz_offset = parse_date[-1]
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


def nntp_to_mbox(lst_name, frm, date, sub, msg, body, last):
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

        save_parsed_lists(lst_name, last)

    logging.info('Quit')
    sys.exit()


def main():
    # Get the configuration data from liststat.CONF_FILE_PATH.
    conf_info, total_lists = liststat.get_configuration(liststat.CONF_FILE_PATH, 
                                                                pipermail=False)
    parsed_lists = get_parsed_lists()

    counter = 0
    for names, lists in conf_info.iteritems():
        for lst in lists:                      
            logging.info('\tList %d of %d' % (counter+1, total_lists))

            # list-name@list-url redirects to the corresponding Gmane group.
            url, lst_name = lst.rsplit('/', 1)
            # Strip the 'http://' from the URL.
            if url.startswith('http://'):
                url = url[len('http://'):]

            list_url = '{0}@{1}'.format(lst_name, url)

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
                logging.error('Unable to connect to the NNTP server')
                continue

            try:
                response, count, first, last, name = conn.group(group_name)
            except nntplib.NNTPTemporaryError as detail:
                logging.error(detail)
                counter += 1
                continue

            first = int(first)
            last = int(last)

            logging.info("Group '%s' has %s articles" % (name, count))

            # Get the information for the list from the previous run, if it exists
            # and then compare to see whether new articles are present and if yes,
            # then download the new articles only.
            if lst_name in parsed_lists:
                last_run = int(parsed_lists[lst_name]['end'])
                if last_run == last:
                    logging.info('List is up to date, nothing to download')
                    counter += 1
                    continue
                if last > last_run:
                    first = last_run+1

            logging.info('Downloading messages from %d - %d' % (first, last))
            count = (last - first)+1
            logging.info('Fetching message bodies for %d articles...' % count)

            msg_range = str(first) + '-' + str(last)

            from_lst = []
            date_lst = [] 
            subject_lst = []
            msg_id_lst = []

            resp, from_lst = conn.xhdr('From', msg_range)
            resp, date_lst = conn.xhdr('Date', msg_range)
            resp, subject_lst = conn.xhdr('Subject', msg_range)

            body = []
            for i in range(first, last+1):
                try:
                    resp, article_id, msg_id, msg = conn.body(str(i))
                    msg_id_lst.append(msg_id)
                    body.append('\n'.join(msg))
                except nntplib.NNTPTemporaryError as detail:
                    continue

            logging.info('Fetched the message bodies')

            from_lst = [frm for (article_id, frm) in from_lst]
            date_lst = [date for (article_id, date) in date_lst]
            subject_lst = [subject for (article_id, subject) in subject_lst]

            nntp_to_mbox(lst_name, 
                        from_lst, date_lst, subject_lst, msg_id_lst, 
                        body, last)

            counter += 1


if __name__ == '__main__':
    liststat.start_logging()

    if not os.path.isfile(NNTP_CONF_SAVE_PATH):
        open(NNTP_CONF_SAVE_PATH, 'w').close()
    
    logging.info('\t\tStarting NNTPListStat')

    main()
