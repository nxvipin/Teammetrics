#! /usr/bin/env python

"""Fetch messages from Gmane over NNTP and create mbox archives.

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
import updatenames

NNTP_CONF_FILE = 'nntplists.hash'
NNTP_CONF_SAVE_PATH = os.path.join(liststat.ARCHIVES_SAVE_DIR, 
                                  liststat.PROJECT_DIR,
                                  NNTP_CONF_FILE)

ARCHIVES_FILE_PATH = liststat.ARCHIVES_FILE_PATH

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


def asctime_update(mail_asctime, msg_id):
    """Returns a timestamp formatted to asctime and with the timezone adjusted.
    
    example:
        Sat 4, Jun 2011 17:36:40 +0530

    will return:
        Sat Jun  4 12:06:40 2011
    """

    # Parse date according to RFC 2822 but with the timezone info. 
    parse_date = email.utils.parsedate_tz(mail_asctime)
    # Get the timezone offset in seconds and create a timezone delta.
    # For some messages, there is invalid time zone data, so we set the
    # time zone to UTC. This is not precise but it suits our purpose
    # well because we are not bothered about the exact time (though we
    # do save it) but the month and the year. 
    try:
        tz_offset = parse_date[-1]
    except TypeError:
        logging.error('Invalid time zone for Message-ID: %s' % msg_id)
        logging.info('Setting time zone to UTC')
        tz_offset = 0

    if tz_offset is None:
        logging.error('Invalid time zone for Message-ID: %s' % msg_id)
        logging.info('Setting time zone to UTC')
        tz_offset = 0

    tz = datetime.timedelta(seconds=tz_offset)

    # For messages that have a badly formatted Date header,
    # return None and skip the message.
    try:
        asctime = datetime.datetime(*parse_date[:7], tzinfo=None)
    except (ValueError, TypeError):
        return None

    # The adjusted timezone according to the offset.
    asctime_updated = asctime - tz

    # Return an asctime string.
    try:
        return time.asctime(asctime_updated.timetuple())
    except ValueError:
        return None


def format_mail_name(from_field):
    """Returns a formatted version of the 'From' field.

        John Doe <john@doe.com>
    will return:
        john at doe.com (John Doe)

    In some cases, the 'From' field can also be formatted as:
        john@doe.com (John Doe)

    We handle both the cases but the returned string is the same.  
    """

    # No regex!
    if from_field.startswith('<') and from_field.endswith('>'):
        email_start_pos = from_field.find("<")
        email_end_pos = from_field.find(">")
        email = from_field[email_start_pos+1:email_end_pos]
        name = email.strip("""'"<""")
        return email, name

    if from_field.endswith('>'):
        # Get the position of < and > to parse the email.
        email_start_pos = from_field.find("<")
        email_end_pos = from_field.find(">")
        email = from_field[email_start_pos+1:email_end_pos]
        
        name_raw = from_field[:email_start_pos-1].strip()
        name = name_raw.strip("""'">""")
        return email, name

    # For the second case.
    elif from_field.endswith(')'):
        # Get the position of ( and ) to parse the name.
        name_start_pos = from_field.find("(")
        name_end_pos = from_field.find(")")
        name_raw = from_field[name_start_pos+1: name_end_pos]
        name = name_raw.strip("""'">""")

        email = from_field[:name_start_pos-1]
        return email, name

    # This is for badly formatted From headers.
    else:
        return '', ''


def nntp_to_mbox(lst_name, lst_url, frm, date, sub, msg, body, first, last):
    """Convert the information fetched from the NNTP server to a mbox archive."""

    logging.info('Parsing and creating mbox archive for %s' % lst_name)
    mbox_format = """From {0}
From: {1}
Date: {2}
Subject: {3}
Message-ID: {4}

"""
    mbox_file_name = '{0}-{1}-{2}.mbox'.format(lst_name, first, last)
    mbox_file_path = os.path.join(ARCHIVES_FILE_PATH, mbox_file_name)

    with open(mbox_file_path, 'w') as mbox_file:
        for f, d, s, m, b in zip(frm, date, sub, msg, body):

            email, name = format_mail_name(f)
            if not email or not name:
                logging.error('Invalid Name and/or Email for Message-ID: %s' % m)
                continue 

            updated_date = asctime_update(d, m)
            if updated_date is None:
                logging.error('Invalid Date header for Message-ID: %s' % m)
                continue

            f_one = '{0}  {1}'.format(email, updated_date)
            f_two = '{0} ({1})'.format(email, name)
          
            mbox_file.write(mbox_format.format(f_one, f_two, d, s, m)) 
            mbox_file.write(b)
            mbox_file.write('\n')

    logging.info('mbox archive saved for %s' % lst_name)
    save_parsed_lists(lst_name, last)

    # Call liststat that will parse the mbox created.
    liststat.parse_and_save({lst_url: mbox_file_path}, nntp=True)


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
            except socket.error as detail:
                logging.error(detail)
                continue
            except nntplib.NNTPTemporaryError as detail:
                logging.error(detail)
                continue

            try:
                response, count, first, last, name = conn.group(group_name)
            except (nntplib.NNTPTemporaryError, EOFError) as detail:
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
                    logging.info('Last run ended at message %d', last_run)
                    first = last_run+1

            logging.info('Fetching message bodies for '
                                            'articles %d - %d' % (first, last))

            msg_range = str(first) + '-' + str(last)

            from_lst = []
            date_lst = [] 
            subject_lst = []
            msg_id_lst = []

            resp, from_lst = conn.xhdr('From', msg_range)
            resp, date_lst = conn.xhdr('Date', msg_range)
            resp, subject_lst = conn.xhdr('Subject', msg_range)

            # A list of numbers with breaks at 100 that will be used for
            # logging. This is helpful in cases where lots of messages
            # are to be downloaded so as to make the user aware of the
            # status of the download.
            logging_counter = [i for i in range(last) if not i % 100]

            body = []
            msg_counter = 1
            logging.info('Updating message count...')
            logging.info('At message: ')
            for i in range(first, last+1):
                try:
                    resp, article_id, msg_id, msg = conn.body(str(i))
                    msg_id_lst.append(msg_id)
                    body.append('\n'.join(msg))
                    # Log the count.
                    if i in logging_counter:
                        logging.info('\t%d' % i)
                    msg_counter += 1
                except nntplib.NNTPTemporaryError as detail:
                    continue

            logging.info('Fetched %d message bodies', msg_counter-1)

            from_lst = [frm for (article_id, frm) in from_lst]
            date_lst = [date for (article_id, date) in date_lst]
            subject_lst = [subject for (article_id, subject) in subject_lst]

            nntp_to_mbox(lst_name, lst,
                        from_lst, date_lst, subject_lst, msg_id_lst, 
                        body, first, last)

            counter += 1

    logging.info('Quit')
    sys.exit()
 

if __name__ == '__main__':
    liststat.start_logging()

    if not os.path.isfile(NNTP_CONF_SAVE_PATH):
        open(NNTP_CONF_SAVE_PATH, 'w').close()
    
    logging.info('\t\tStarting NNTPListStat')

    main()
