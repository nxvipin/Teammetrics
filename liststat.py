#! /usr/bin/env python

"""Generates mailing list statistics for measuring team performance.

This script downloads mbox archives for the mailing list(s) specified, parses
them and generates statistical data about the most active contributors, which
is calculated using various metrics such as:

    - frequency of the 'From' header,
    - the raw length of the message body,
    - the length of the message body excluding quoted lines (>)
    and blank lines (individually).

This script works for any mailing list that runs on GNU Mailman and where 
Pipermail is used as the mail archiver. You just need to specify the list URL
and the script will automatically download all the mbox archives, parse them
and generate the data required. The data generated is stored in a mapping, so 
it's easy to output it in the format you desire. 
"""

import os
import re
import sys
import csv
import gzip
import email
import logging
import mailbox
import hashlib
import urllib2
import urlparse
import datetime
import collections
import ConfigParser

import psycopg2
import BeautifulSoup

import spamfilter

PROJECT_DIR = 'teammetrics'

CONF_FILE = 'listinfo.conf'
CONF_SAVE_DIR = '/etc'
CONF_PATH = os.path.join(CONF_SAVE_DIR, PROJECT_DIR) 
CONF_FILE_PATH = os.path.join(CONF_PATH, CONF_FILE)

ARCHIVES_SAVE_DIR = '/var/cache'
ARCHIVES_FILE_PATH = os.path.join(ARCHIVES_SAVE_DIR, PROJECT_DIR)

HASH_FILE = 'lists.hash' 
HASH_FILE_PATH = os.path.join(ARCHIVES_SAVE_DIR, PROJECT_DIR, HASH_FILE)

LOG_FILE = 'liststat.log'
LOG_SAVE_DIR = '/var/log'
LOG_PATH = os.path.join(LOG_SAVE_DIR, PROJECT_DIR)
LOG_FILE_PATH = os.path.join(LOG_PATH, LOG_FILE)

DATABASE = {'name': 'liststat'}
            

def is_root():
    """Check if the user has root privileges."""
    # If the user doesn't have root privileges return False. We plan to fix 
    # this later by creating a teammetrics group.
    return False if os.getuid() else True


def write_checksum(hashes):
    """Write the hashes generated from the downloaded mbox archives."""
    with open(HASH_FILE_PATH, 'a') as f:
        writer = csv.writer(f, delimiter=':')
        writer.writerows(hashes.iteritems())
    logging.info('Done writing checksums')


def get_checksum():
    """Read the hashes for the mbox file from HASH_FILE."""
    hashes = {}
    with open(HASH_FILE_PATH) as f:
        reader = csv.reader(f, delimiter=':')
        try:
            for row in reader:
                hashes[row[0]] = row[1]
        except (csv.Error, IndexError) as detail:
            logging.error(detail)
            sys.exit()

    return hashes


def generate_checksum(path, name):
    """Return a mapping of a mbox archive to its SHA-1 checksum.

    This function returns SHA-1 checksum of a mbox archive thus maintaining
    consistency and reducing redundancy as the checksum is compared before
    downloading or parsing the archive.
    """

    mbox_hash = {}
    with open(path) as f:
        hash_object = hashlib.sha1()
        hash_object.update(f.read())
        mbox_hash[name] = hash_object.hexdigest()
        
    return mbox_hash


def get_current_month():
    """Return the current month and year."""
    today = datetime.date.today()
    # Append the .txt.gz extension to match the extension format of Pipermail's
    # extension format. %Y is the current year and %B the current month. 
    current_month = today.strftime("%Y-%B") + '.txt.gz'
    return current_month


def get_configuration():
    """Read the lists to be parsed from the configuration file.
 
    This function returns a mapping of list-name to list-addresses. In case
    there are multiple lists per list-name, a list of list-addresses is used
    as the value for the list-name key. 
    """

    config = ConfigParser.SafeConfigParser()
    try:
        config.read(CONF_FILE_PATH)
    except ConfigParser.Error as detail:
        logging.error(detail)
    # Get the names for the mailing lists from the config file.
    sections = [section for section in config.sections()]

    # Create a mapping of the list name to the address(es).
    mailing_list_parse = {}
    for section in sections:
        mailing_list = []
        # In case the url and lists options are not found, skip the section.
        try:
            base_url = config.get(section, 'url')
            list_ = config.get(section, 'lists').splitlines()
        except ConfigParser.NoOptionError as detail:
            logging.error(detail)
            continue
        if not base_url:
            logging.error('Base URL cannot be empty. Skipping list %s' % section)
            continue
        if not list_:
            logging.error('List URL cannot be empty. Skipping list %s' % section)
            continue
        # Just in case someone forgot to append the /.
        for each_list in list_:
            if base_url.endswith('/'):
                mailing_list.append('{0}{1}'.format(base_url, each_list))
            else:
                mailing_list.append('{0}/{1}'.format(base_url, each_list))
        # Mapping of list-name to list URL (or a list of list-URLs).
        mailing_list_parse[section] = mailing_list

    return mailing_list_parse


def parse_and_save(mbox_files, mbox_hashes):
    """Parse the mbox archives to extract the required information.

    Opens each local mbox specified by mbox_files and extracts the required
    information that is then saved to a database.
    """

    # Connect to the database.
    conn = psycopg2.connect(database=DATABASE['name'])
    cur = conn.cursor()

    for url, files in mbox_files.iteritems():
        mbox_ = mailbox.mbox(files)
        for message in mbox_:
            # Name of the mailing list.
            mailing_list = os.path.basename(files).split('.')[0]
            project = mailing_list.rsplit('-', 2)[0]

            # The 'From' field value returns a string of the format:
            #   email-address (Name)
            # from which the sender's name and email address is extracted.
            from_field = message['From']
            if from_field is None:
                continue

            name_start_pos = from_field.find("(")
            name_end_pos = from_field.find(")")
            raw_name = from_field[name_start_pos+1:name_end_pos]
            # Resolve the encodings.
            decoded_name = email.header.decode_header(raw_name)
            name = u" ".join([unicode(text, charset or 'ascii') 
                                        for text, charset in decoded_name])

            # The email address of the sender.
            email_addr_raw = from_field[:name_start_pos-1]
            email_addr = ''.join(email_addr_raw.replace('at', '@').split())

            # The date the message was sent.
            get_date = message['Date']
            parsed_date = email.utils.parsedate(get_date)
            format_date = datetime.datetime(*parsed_date[:4])
            archive_date = format_date.strftime("%Y-%m-%d")
            
            subject = ' '.join(message['Subject'].split())

            name, subject, reason = spamfilter.check_spam(name, subject)

            today_ = datetime.date.today()
            today_date = today_.strftime("%Y-%m-%d")

            # Get the message body. 
            payload = message.get_payload()
            # The lines in the message body excluding blank lines. 
            msg_blank = [line for line in payload.splitlines() if line]
            msg_blank_len = len(msg_blank)
            # The lines in the message body excluding quotes (starting with >).
            msg_quotes_len = len([line for line in msg_blank
                                                if not line.startswith('>')])
            # The number of characters in the message body.
            msg_raw_len = len(''.join(element for element in msg_blank))

            # The netloc from the mailing list URL.
            netloc = urlparse.urlparse(url).netloc

            # Save the required information to the database.
            try:
                cur.execute(
                """INSERT INTO listarchives
                    (project, domain, name, email_addr, subject, archive_date, 
                    today_date, msg_blank_len, msg_quotes_len, msg_raw_len, spam)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    (project, netloc, name, email_addr, subject, archive_date, 
                    today_date, msg_blank_len, msg_quotes_len, msg_raw_len, spam)
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                continue

            conn.commit()
        logging.info('Done parsing %s' % mailing_list)

    cur.close()
    conn.close()

    # Write the checksums of the download mbox archives.
    if mbox_hashes:
        write_checksum(mbox_hashes)

    logging.info('Quit')
    sys.exit()


def main(conf_info): 
    """Fetch the mbox archives from the URLs specified.

        mbox_files      -   mapping of URLs to the path of local mbox archives
                            (in plain text format)
        conf_info       -   mapping of list names to their URLs
        mbox_archives   -   mbox archives in gzip format 
    """ 

    # Calculate the total number of lists by iterating through the values of 
    # conf_info. Note that there are multiple values per key. 
    total_lists = len([item for items in conf_info.values() for item in items])
    if not total_lists:
        logging.error('No lists found to parse as no lists were found')
        sys.exit()

    count = 0
    mbox_files = {}
    mbox_archives = []
    mbox_hashes = {}
    parsed_hash = get_checksum()
    current_month = get_current_month()

    # The conf_info has a mapping of {list-name : [list-url]}. So we go through
    # each value and download the corresponding list.
    for names, lists in conf_info.iteritems():
        for name in names:
            for list_ in lists:
                logging.info('\tList %d of %d' % (count+1, total_lists))
                logging.info("Reading %s" % list_)
                try:
                    url = urllib2.urlopen(list_)
                except (urllib2.URLError, ValueError) as detail:
                    logging.error("Unable to fetch mailing list"
                                                    " archive %s" % detail)
                    count += 1
                    continue                
                response = url.read()

                # Find all the <a> tags ending in '.txt.gz'.
                soup = BeautifulSoup.BeautifulSoup(response)
                parse_dates = soup.findAll('a', href=re.compile('\.txt\.gz$'))
                # Extract the months from the <a> tags. This is used to download
                # the mbox archive corresponding to the months the list was active.
                archive_dates = []
                archive_dates.extend([str(element.get('href')) for element 
                                                                in parse_dates])

                # Download all lists except that of the current month. 
                if current_month in archive_dates:
                    archive_dates.remove(current_month)

                # Skip if there are no dates.
                if not archive_dates:
                    logging.warning('No dates found. Skipping')
                    count += 1
                    continue

                # Download the mbox archives and save them to DIRECTORY_PATH.
                logging.info("Downloading %d mbox archives" % len(archive_dates))
                for date in archive_dates:
                    mbox_url = '{0}/{1}'.format(list_, date)
                    mbox_name = '{0}-{1}'.format(list_.split('/')[-1], date)
                    path_to_archive = os.path.join(ARCHIVES_FILE_PATH, mbox_name)
                    # Open the mbox archive and save it to the local disk.
                    try:
                        mbox = urllib2.urlopen(mbox_url)
                    except urllib2.URLError as detail:
                        logging.error('%s - %s' % (detail, mbox_url))
                        count += 1
                        continue
                    with open(path_to_archive, 'wb') as f:
                        mbox_archives.append(path_to_archive)
                        f.write(mbox.read())
                
                    # Get the SHA-1 hash of the current mbox. 
                    mbox_hash = generate_checksum(path_to_archive, mbox_name)
                    # If the SHA-1 from the already parsed mbox archives is 
                    # equal to the SHA-1 of the current mbox, don't parse the
                    # archive and remove it from mbox_archives.
                    mbox_hash_file = list(set(parsed_hash) & set(mbox_hash))
                    if mbox_hash_file:
                        if parsed_hash[mbox_name] == mbox_hash[mbox_name]:
                            logging.warning("Skipping already downloaded "
                                               "and parsed mbox %s" % mbox_name)
                            mbox_archives.remove(path_to_archive)
                            os.remove(path_to_archive)
                            continue

                    # Extract the mbox file (plain text) from the gzip archive. 
                    mbox_plain_text = '{0}'.format(mbox_name.rsplit('.', 1)[0])
                    mbox_path = os.path.join(ARCHIVES_FILE_PATH, mbox_plain_text)
                    with open(mbox_path, 'w') as gzip_file:
                        temp_file = gzip.open(path_to_archive, 'rb')
                        archive_contents = temp_file.read()
                        gzip_file.write(archive_contents)
                        mbox_files[mbox_url] = mbox_path
                        # Update the hash for the archive downloaded.
                        mbox_hashes.update(mbox_hash)
                        logging.info('Finished downloading %s' % mbox_name)
                count += 1
            break

    # We don't need the mbox archives, so delete them.
    if mbox_archives:
        logging.info('Cleaning up...')
        for archives in mbox_archives:
            os.remove(archives)

    # If nothing to parse, quit.
    if not mbox_files:
        logging.info('Quit: nothing to parse')
        sys.exit()

    # Open each local mbox archive and then parse it.
    parse_and_save(mbox_files, mbox_hashes)


if __name__ == '__main__':
    # Are we root?
    if not is_root():
        sys.exit('Please run this script with root privileges.')
    # Create the directories on first run. NOTE: This will be changed later. 
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)
    if not os.path.isfile(LOG_FILE_PATH):
        open(LOG_FILE_PATH, 'w').close()

    # Initialize the logging.
    logging.basicConfig(filename=LOG_FILE_PATH,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')
    logging.info('\t\tStarting ListStat')

    # Get the configuration.
    conf_info = get_configuration()
    
    # Check whether the DATABASE dictionary is populated.
    for keys, items in DATABASE.iteritems():
        if not items:
            logging.error('Please set a value for DATABASE %s' % keys)
            sys.exit(1)
    # Simulate a connection just to check whether everything is OK.
    try:
        psycopg2.connect(database=DATABASE['name'])
    except psycopg2.Error as detail:
        logging.error(detail)
        sys.exit(1)
    logging.info('Connection to database successful')

    if not os.path.isdir(ARCHIVES_FILE_PATH):
        os.mkdir(ARCHIVES_FILE_PATH)
        logging.info("Directory created '%s'" % ARCHIVES_FILE_PATH)
    if not os.path.isdir(CONF_PATH):
        os.mkdir(CONF_PATH)
        logging.info("Directory created '%s'" % CONF_PATH)
    if not os.path.isfile(CONF_FILE_PATH):
        logging.error("File not found '%s' " % CONF_FILE_PATH)
        sys.exit()
    if not os.path.isfile(HASH_FILE_PATH):
        open(HASH_FILE_PATH, 'w').close()

    main(conf_info)
