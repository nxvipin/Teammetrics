#! /usr/bin/env python

"""Fetches and parses web archives from lists.debian.org."""

import re
import os
import sys
import time
import urllib2
import logging
import datetime
import HTMLParser
import email.header

from BeautifulSoup import BeautifulSoup
import psycopg2

import liststat
import nntpstat

ARCHIVE_SAVE_DIR = '/var/cache/teammetrics/'

BASE_URL = 'http://lists.debian.org/'
FIELDS = ('From', 'Date', 'Subject', 'Message-id')
MESSAGE_FORMAT = """From {0}
From: {1}
Date: {2}
Subject: {3}
Message-ID: <{4}>

"""


def create_mbox(lst_name, mbox_name, name, email_addr, raw_d, updated_d, sub, msg_id, body):
    """Creates mbox archives for a given message article."""
    with open(os.path.join(ARCHIVE_SAVE_DIR, mbox_name), 'a') as f:
        encode_name = email.header.Header(name, 'utf-8')
        encode_subject = email.header.Header(sub, 'utf-8')

        from_one = '{0}  {1}'.format(email_addr, updated_d)
        from_two = '{0} ({1})'.format(email_addr, encode_name)

        f.write(MESSAGE_FORMAT.format(from_one, from_two, raw_d, encode_subject, msg_id))
        f.write(body.encode('utf-8'))
        f.write('\n\n\n')
        f.flush()


def main():
    """Read a list archive message and parse it."""
    conf_info, total_lists = liststat.get_configuration(liststat.CONF_FILE_PATH,
                                                        pipermail=False)
    counter = 0
    for names, lists in conf_info.iteritems():
        for lst in lists:
            lst_name = lst.rsplit('/')[-1]
            logging.info('\tList %d of %d' % (counter+1, total_lists))
            logging.info("Fetching '%s'" % lst_name)

            try:
                url_read = urllib2.urlopen(lst)
            except urllib2.HTTPError as detail:
                logging.error('Invalid list name, skipping')
                counter += 1
                continue

            # Get the links to the archives.
            soup = BeautifulSoup(url_read)
            all_links = soup.findAll('a', href=re.compile('\d'))
            links = [tag['href'] for tag in all_links]

            start = links[0].split('/')[0]
            end = links[-1].split('/')[0]
            logging.info('List archives are from %s to %s' % (start, end))

            for link in links:
                month_url = '{0}{1}/{2}'.format(BASE_URL, lst_name, link)
                try:
                    month_read = urllib2.urlopen(month_url)
                except urllib2.URLError as detail:
                    logging.error('Skipping message, error connecting to lists.debian.org')
                    logging.error('%s' % detail)
                    continue

                soup = BeautifulSoup(month_read)
                message_links = soup.findAll('a', href=re.compile('msg'))
                messages = [links['href'] for links in message_links]

                for message in messages:
                    # Extract the month from the string:
                    #   <list-name>/<year>/<list-name>-<year><month>/threads.html
                    # and then construct the message URL:
                    #   <list-name>/<year>/<month>/<message-url>
                    year_month = month_url.split('/')[-2].rsplit('-')[-1]
                    year = year_month[:-2]
                    month = year_month[-2:]
                    message_url = '{0}{1}/{2}/{3}/{4}'.format(BASE_URL, lst_name, 
                                                            year, month, message)

                    try:
                        message_read = urllib2.urlopen(message_url)
                    except urllib2.URLError as detail:
                        logging.error('Skipping message, error connecting to lists.debian.org')
                        logging.error('%s' % detail)
                        continue

                    soup = BeautifulSoup(message_read)
                    # Now we are at a single message, so parse it.
                    body = soup.body.ul
                    all_elements = body.findAll('li')
                    all_elements_text = [element.text for element in all_elements if element.text.startswith(FIELDS)]
                    all_elements_text.sort()

                    # The list should have four elements (fields): 
                    #   From, Date, Subject, Message-id.
                    # If not, this is due to a badly formed header, so just continue.
                    if len(all_elements_text) != 4:
                        continue

                    # Date.
                    raw_date = all_elements_text[0].split(':', 1)[1].strip()
                    # Name, Email.
                    name_email = all_elements_text[1].split(':')[1]
                    # Message-id.
                    message_id = all_elements_text[2].split(':', 1)[1].replace('&lt;', '').replace('&gt;', '').strip()
                    # Subject.
                    subject = all_elements_text[3].split(':', 1)[1].strip()

                    # Format the 'From' field to return the name and email address.
                    #   Foo Bar &lt;foo@bar.com&gt; 
                    try:
                        if name_email.endswith(')'):
                            email_raw, name_raw = name_email.split('(', 1)
                            name = name_raw.strip('()')
                            email = email_raw
                        else:
                            name_raw, email_raw = name_email.strip().rsplit(None, 1)
                            # Name.
                            if name_raw.startswith('&quot;') or name_raw.endswith('&quot;'):
                                name = name_raw.replace('&quot;', '')
                            else:
                                name = name_raw
                            # Email.
                            if email_raw.startswith('&lt;') and email_raw.endswith('&gt;'):
                                email = email_raw.replace('&lt;', '').replace('&gt;', '')
                            else:
                                email = email_raw
                    except ValueError:
                        # The name is the same as the email address.
                        name = email = name_email.replace('&lt;', '').replace('&gt;', '')

                    # Some names have the form: LastName, FirstName. 
                    if ',' in name:
                        name = ' '.join(e for e in reversed(name.split())).replace(',', '').strip()

                    parser = HTMLParser.HTMLParser()
                    name = parser.unescape(name).strip()
                    email = email.replace('&lt;', '').replace('&gt;', '')

                    today_raw = datetime.date.today()
                    today_date = today_raw.strftime('%Y-%m-%d')
                    updated_date = nntpstat.asctime_update(raw_date, message_id)
                    if updated_date is None:
                        logging.error('Unable to decode date, skipping message %s' % message_id)
                        continue

                    body_unescape = HTMLParser.HTMLParser()
                    body = body_unescape.unescape(soup.body.pre.text)

                    mbox_name = '{0}-{1}{2}'.format(lst_name, year, month)
                    create_mbox(lst_name, mbox_name, 
                                name, email, 
                                raw_date, updated_date,
                                subject, message_id, body)

            counter += 1

    logging.info('Quit')
    sys.exit()


if __name__ == '__main__':
    liststat.start_logging()
    logging.info('\t\tStarting Web Archive Parser')

    main()
