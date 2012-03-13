#! /usr/bin/env python

"""Creates mbox archives for the lists archives from lists.debian.org"""

import re
import os
import sys
import time
import urllib2
import logging
import datetime
import HTMLParser
import ConfigParser

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment
import psycopg2

import nntpstat
import liststat
import spamfilter
import updatenames

BASE_URL = 'http://lists.debian.org/'
FIELDS = ('From', 'Date', 'Subject', 'Message-id', 'In-reply-to', 'References')
CONFIG_FILE = '/var/cache/teammetrics/mboxarchiveparser.status'
LOG_FILE = '/var/log/teammetrics/mboxliststat.log'
ARCHIVE_SAVE_DIR = '/var/cache/teammetrics/archivemboxes'


def create_mbox(lst_name, mbox_name, name, email_addr, raw_d, updated_d, sub, msg_id, body, in_reply_to, references):
    """Creates mbox archives for a given message article."""
    with open(os.path.join(ARCHIVE_SAVE_DIR, mbox_name), 'a') as f:
        encode_name = name.encode('utf-8')
        encode_subject = sub.encode('utf-8')
        body = body.encode('utf-8')

        from_one = '{0}  {1}'.format(email_addr, updated_d)
        from_two = '{0} ({1})'.format(email_addr, encode_name)

        f.write("From {0}\n".format(from_one))
        f.write("From: {0}\n".format(from_two))
        f.write("Date: {0}\n".format(raw_d))
        f.write("Subject: {0}\n".format(sub))
        f.write("Message-ID: <{0}>\n".format(msg_id))
        if in_reply_to:
            f.write("In-Reply-To: {0}\n".format(in_reply_to))
        if references:
            f.write("References: {0}\n".format(references))
        f.write('\n')
        f.write(body)
        f.write('\n')
        f.flush()


def read_config(name):
    """Read the configuration from CONFIG_FILE.
    
    Reads the configuration for list_name from CONFIG_FILE and if the list is
    present, returns the information from the last parsed messages. This helps 
    resume the ArchiveParser from the last run.
    """

    parser = ConfigParser.SafeConfigParser()
    parser.read(CONFIG_FILE)

    if parser.has_section(name):
        return parser.get(name, 'year'), parser.get(name, 'month'), parser.get(name, 'message')
    else:
        return ()


def write_config(name, year, month, message):
    """Write the configuration file for the current run."""
    parser = ConfigParser.SafeConfigParser()
    parser.read(CONFIG_FILE)

    if not parser.has_section(name):
        parser.add_section(name)
    parser.set(name, 'year', year)
    parser.set(name, 'month', month)
    parser.set(name, 'message', message)
    parser.write(open(CONFIG_FILE, 'w'))


def fetch_message_links(soup):
    """Parse the page and return links to individual messages."""
    message_links = soup.findAll('a', href=re.compile('msg'))
    return [links['href'] for links in message_links]


def check_next_page(month_url):
    """Returns the total pages for a month in a list."""
    total = []
    counter = 2
    added_url = False
    open_url = month_url.rsplit('/', 1)[0]
    while True:
        try:
            current_url = '{0}/thrd{1}.html'.format(open_url, counter)
            urllib2.urlopen(current_url)
            if not added_url:
                total.append(month_url)
            total.append(current_url)
            added_url = True
            counter += 1
        except urllib2.URLError:
            break

    return total


def make_multiple_lines(field):
    return '\n'.join('{0}>'.format(b) if a==0 
                    else '\t<{0}'.format(b) 
                    for (a, b) in enumerate(field.rsplit('<')) if b)


def main():
    conf_info, total_lists = liststat.get_configuration(liststat.CONF_FILE_PATH,
                                                        pipermail=False)
    counter = 0
    skipped_messages = 0
    fetched_messages = 0
    for names, lists in conf_info.iteritems():
        for lst in lists:
            list_fetched_messages = 0
            lst_name = lst.rsplit('/')[-1]

            # In consecutive runs, the already parsed message are skipped without even being fetched.
            # Everything is set to type: Unicode because that is what BeautifulSoup returns.
            config_data = tuple(unicode(ele) for ele in read_config(lst_name))
            if config_data:
                c_year = config_data[0]
                c_month = config_data[1]
                c_message = config_data[2]
                year_month_flag = message_flag = True
            else:
                year_month_flag = message_flag = False

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
            all_links = soup.findAll('a', href=re.compile('threads.html'))
            links = [tag['href'] for tag in all_links]

            if year_month_flag:
                logging.info('Last run was on %s-%s/%s' % (c_year,  c_month, c_message))
                last_link = unicode('{0}/{1}-{0}{2}/threads.html'.format(c_year, lst_name, c_month))
                links = links[links.index(last_link):]
                year_month_flag = False

            all_months = soup.body.findAll('ul')[1].findAll('li')
            start = all_months[0].text.split(None, 1)[0]
            end = all_months[-1].text.split(None, 1)[0]
            logging.info('List archives are from %s to %s' % (start, end))

            for link in links:
                # Get the year for which the messages are to be fetched.
                month_url = '{0}{1}/{2}'.format(BASE_URL, lst_name, link)
                year_month = link.split('/')[-2].rsplit('-')[-1]
                year = year_month[:-2]
                month = year_month[-2:]

                try:
                    month_read = urllib2.urlopen(month_url)
                except urllib2.URLError as detail:
                    logging.error('Skipping month %s: unable to connect to lists.d.o' % link)
                    logging.error('%s' % detail)
                    continue

                soup = BeautifulSoup(month_read)

                messages = []
                # There are multiple pages in an archive, check for them.
                all_pages_month = check_next_page(month_url)
                if all_pages_month:
                    for each_month in all_pages_month:
                        page_soup = BeautifulSoup(urllib2.urlopen(each_month))
                        messages.extend(fetch_message_links(page_soup))
                else:
                    messages.extend(fetch_message_links(soup))

                if message_flag:
                    upto_messages = [unicode('msg{0:05}.html'.format(e)) 
                                        for e in range(int(c_message[3:].strip('.html'))+1)]
                    messages = list(set(messages) - set(upto_messages))
                    message_flag = False

                # Sort the list before starting so as to match up to the notion of upto_messages.
                messages.sort()
                for message in messages:
                    # Construct the message URL:
                    message_url = '{0}{1}/{2}/{3}/{4}'.format(BASE_URL, lst_name, 
                                                                year, month, message)
                    try:
                        message_read = urllib2.urlopen(message_url)
                    except urllib2.URLError as detail:
                        logging.error('Skipping message: unable to connect to lists.d.o')
                        skipped_messages += 1
                        continue

                    soup = BeautifulSoup(message_read)

                    # Now we are at a single message, so parse it.
                    body = soup.body.ul
                    all_elements = body.findAll('li')
                    # Fetch the text of all elements in FIELDS.
                    all_elements_text = [element.text for element in all_elements if element.text.startswith(FIELDS)]
                    # Create a mapping of field to values.
                    fields = {}
                    for element in all_elements_text:
                        field, value = element.split(':', 1)
                        fields[field.strip()] = value.strip()

                    # From field.
                    # In case of a missing 'From' field, just skip because we don't need to parse the message then.
                    if 'From' not in fields:
                        continue

                    # Name, Email parsing starts here.
                    # Format the 'From' field to return the name and email address.
                    #   Foo Bar &lt;foo@bar.com&gt; 
                    name_email = fields.get('From')
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

                    # Subject field.
                    subject = fields.get('Subject', '')

                    # Date field.
                    date = fields.get('Date')
                    if date is not None:
                        # Let's parse the date now and fetch the day the message was sent.
                        day_find = re.findall(r'\d{1,2}', date)
                        # Can't parse the date, so set it to a random value.
                        if day_find:
                            day = day_find[0]
                        else:
                            day = '15'
                    # If there is no 'Date' field.
                    else:
                        day = '15'
                    final_day = day
                    final_month = month
                    final_year = year

                    final_date = '{0}-{1}-{2}'.format(final_year, final_month, final_day)
                    # Before storing the date, ensure that it is proper. If not,
                    # this is usually due to the issue of the last day of a given
                    # month being counted in the next. So default the day to 1.
                    try:
                        time.strptime(final_date, '%Y-%m-%d')
                    except ValueError:
                        final_date = '{0}-{1}-1'.format(final_year, final_month)

                    today_raw = datetime.date.today()
                    today_date = today_raw.strftime('%Y-%m-%d')

                    # Message-id field.
                    # If no Message-id field found, generate a random one.
                    message_id = fields.get('Message-id', u'{0}-{1}-{2}@spam.lists.debian.org'.format(name.replace(' ', ''),
                                                                                                      final_month, final_day))
                    message_id = message_id.replace('&lt;', '').replace('&gt;', '')

                    # In-reply-to and References field.
                    in_reply_to = fields.get('In-reply-to', '')
                    in_reply_to = HTMLParser.HTMLParser().unescape(in_reply_to)
                    references = HTMLParser.HTMLParser().unescape(fields.get('References', ''))

                    if '><' in references:
                        references = make_multiple_lines(references)

                    is_spam = False
                    # Run it through the spam filter.
                    name, subject, reason, spam = spamfilter.check_spam(name, subject)
                    # If the message is spam, set the is_spam flag.
                    if spam:
                        is_spam = True
                        logging.warning('Possible spam: %s. Reason: %s' % (message_id, reason))

                    for element in soup.findAll('pre'):
                        body =  list(element.findAll(text=True))

                    try:
                        body = ''.join(HTMLParser.HTMLParser().unescape(e) for e in body)
                    except TypeError:
                        # For HTML messages, extract the text.
                        start_message = soup.find(text=lambda e: isinstance(e, Comment) and e==u'X-Body-of-Message')
                        body = []
                        for e in start_message.findAllNext(text=True):
                            if e == u'X-Body-of-Message-End':
                                break
                            body.append(e)
                        body = HTMLParser.HTMLParser().unescape(''.join(body))
    
                    updated_date = nntpstat.asctime_update(date, message_id)
                    if updated_date is None:
                        logging.error('Unable to decode date, skipping message %s' % message_id)
                        continue

                    mbox_name = '{0}-{1}{2}'.format(lst_name, year, month)
                    create_mbox(lst_name, mbox_name, 
                                name, email, 
                                date, updated_date,
                                subject, message_id, body, in_reply_to, references)

                    list_fetched_messages += 1
                    fetched_messages += 1

                if messages: 
                    write_config(lst_name, final_year, final_month, message)

            logging.info("Finished processing '%s' (%s messages)" % (lst_name, list_fetched_messages))
            counter += 1

    if fetched_messages:
        logging.info('Fetched %s messages in the current run' % fetched_messages)
    else:
        logging.info('No messages were fetched in the current run')

    if skipped_messages:
        logging.info('Skipped %s messages in the current run' % skipped_messages)

    logging.info('Quit')
    sys.exit()


if __name__ == '__main__':
    liststat.start_logging(logfilepath=LOG_FILE)
    logging.info('\t\tStarting Archive Parser (mbox)')
    main()
