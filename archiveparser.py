#! /usr/bin/env python

"""Fetches and parses web archives from lists.debian.org."""

import re
import time
import datetime
import urllib2
import logging

from BeautifulSoup import BeautifulSoup
import psycopg2

import liststat

BASE_URL = 'http://lists.debian.org/'
FIELDS = ('From', 'Date', 'Subject', 'Message-id')


def main(conn, cur):
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
                month_read = urllib2.urlopen(month_url)

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

                    message_read = urllib2.urlopen(message_url)
                    soup = BeautifulSoup(message_read)

                    # Now we are at a single message, so parse it.
                    body = soup.body.ul
                    all_elements = body.findAll('li')
                    all_elements_text = [str(element.text) for element in all_elements if str(element.text).startswith(FIELDS)]

                    all_elements_text.sort()

                    raw_date = all_elements_text[0].split(':', 1)[1].strip()
                    name_email = all_elements_text[1].split(':')[1]
                    message_id = all_elements_text[2].split(':')[1].strip(' &lgt;')
                    subject = all_elements_text[3].split(':')[1]

                    # Let's parse the date now.
                    try:
                        date = time.strptime(raw_date[:25], '%a, %d %b %Y %H:%M:%S')
                    except ValueError:
                        logging.warning('Possible spam: %s' % message_id)
                        continue

                    message_year = date.tm_year
                    message_month = date.tm_mon

                    if (message_year != year) or (message_month != month):
                        logging.warning('Possible spam: date mismatch in message %s' % message_id)
                        # We default the date to 15 of the month (random).
                        final_day = '15'
                        final_month = month
                        final_year = year
                    else:
                        final_day = date.tm_mday
                        final_month = month
                        final_year = year

                    # Format the 'From' field to return the name and email address.
                    #   Foo Bar &lt;foo@bar.com&gt; 
                    name_raw, email_raw = name_email.strip().rsplit(None, 1)
                    name = name_raw.strip(' &quot;')
                    email = email_raw[4:-4]
                    final_date = '{0}-{1}-{2}'.format(final_year, final_month, final_day)

                    today_raw = datetime.date.today()
                    today_date = today_raw.strftime('%Y-%m-%d')

                    # Populate the database.
                    try:
                        cur.execute(
                                """INSERT INTO listarchives
                        (project, domain, name, email_addr, subject, message_id, archive_date, today_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                    (lst_name, 'lists.debian.org', name, email, subject, message_id, final_date, today_date)
                                    )
                    except psycopg2.DataError as detail:
                        conn.rollback()
                        logging.error(detail)
                        continue
                    conn.commit()

            counter += 1


if __name__ == '__main__':
    liststat.start_logging()
    logging.info('\t\tStarting Web Archive Parser')

    DATABASE = liststat.DATABASE
    # Connect to the database.
    try:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['defaultport'])
    except psycopg2.OperationalError:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['port'])
    cur = conn.cursor()

    main(conn, cur)
