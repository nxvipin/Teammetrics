#! /usr/bin/env python

"""Generates mailing list statistics for GNU Mailman lists.

This script downloads mbox archives for the mailing list(s) specified, parses
them and generates statistical data about the most active contributors, which
is calculated using the metrics:

    - frequency of the From header,
    - the raw length of the message body,
    - the length of the message body excluding quoted lines (>), blank lines
    and signatures (individually).

This script works for any mailing list that runs on GNU Mailman and where
Pipermail is used as the mail archiver but the parse_and_save function can be
used to parse any mailbox. You just need to specify the list URL and the script
will automatically download all the mbox archives, parse them and generate the
information required. The information gathered is then stored in a database
which you can query to get the specific statistics you desire.
"""

import os
import re
import sys
import gzip
import email
import logging
import hashlib
import mailbox
import urllib2
import urlparse
import datetime
import ConfigParser

import chardet
import psycopg2
import BeautifulSoup

import spamfilter
import updatenames


PROJECT_DIR = 'teammetrics'

CONF_FILE = 'listinfo.conf'
CONF_SAVE_DIR = '/etc'
CONF_PATH = os.path.join(CONF_SAVE_DIR, PROJECT_DIR) 
CONF_FILE_PATH = os.path.join(CONF_PATH, CONF_FILE)

ARCHIVES_SAVE_DIR = '/var/cache'
ARCHIVES_FILE_PATH = os.path.join(ARCHIVES_SAVE_DIR, PROJECT_DIR)

HASH_FILE = 'lists.hash' 
HASH_FILE_PATH = os.path.join(ARCHIVES_SAVE_DIR, PROJECT_DIR, HASH_FILE)

LOG_FILE = 'aliothliststat.log'
LOG_SAVE_DIR = '/var/log'
LOG_PATH = os.path.join(LOG_SAVE_DIR, PROJECT_DIR)
LOG_FILE_PATH = os.path.join(LOG_PATH, LOG_FILE)

DATABASE = {
            'name':        'teammetrics',
            'defaultport': 5432,
            'port':        5441, # ... use this on blends.debian.net / udd.debian.net
           }
            

def write_parsed_lists(lists):
    """Write the lists parsed from the downloaded mbox archives."""
    with open(HASH_FILE_PATH, 'a') as f:
        for lst in lists:
            f.write(lst)
            f.write('\n')

    logging.info('Done writing current lists')


def get_parsed_lists():
    """Read the already parsed lists from HASH_FILE."""
    parsed_lists = []
    with open(HASH_FILE_PATH) as f:
        parsed_lists = [line.strip() for line in f.readlines()]

    return parsed_lists


def get_current_month():
    """Return the current month and year."""
    today = datetime.date.today()
    # Append the .txt.gz extension to match the extension format of Pipermail's
    # extension format. %Y is the current year and %B the current month. 
    current_month = today.strftime("%Y-%B") + '.txt.gz'
    return current_month


def get_configuration(config_file_path=CONF_FILE_PATH, pipermail=True):
    """Read the lists to be parsed from the configuration file.
 
    This function returns a mapping of list-name to list-addresses. In case
    there are multiple lists per list-name, a list of list-addresses is used
    as the value for the list-name key. 
    """

    config = ConfigParser.SafeConfigParser()
    try:
        config.read(config_file_path)
    except ConfigParser.Error as detail:
        logging.error(detail)
    # Get the names for the mailing lists from the config file.
    sections = config.sections()

    # Create a mapping of the list name to the address(es).
    mailing_list_parse = {}
    for section in sections:
        mailing_list = []
        # In case the url and lists options are not found, skip the section.
        try:
            base_url = config.get(section, 'url')
            lists = config.get(section, 'lists').splitlines()
        except ConfigParser.NoOptionError as detail:
            logging.error(detail)
            continue
        if not base_url:
            logging.error('Base URL cannot be empty. Skipping list %s' % section)
            continue
        if not lists:
            logging.error('List URL cannot be empty. Skipping list %s' % section)
            continue

        # If pipermail is True, skip the URLs that don't have Pipermail in them.
        # This is used to filter the lists that use NNTP for parsing. 
        if pipermail:
            if not 'pipermail' in base_url:
                continue
        else:
            if 'pipermail' in base_url:
                continue
        
        # Just in case someone forgot to append the /.
        for each_list in lists:
            if base_url.endswith('/'):
                mailing_list.append('{0}{1}'.format(base_url, each_list))
            else:
                mailing_list.append('{0}/{1}'.format(base_url, each_list))
        # Mapping of list-name to list URL (or a list of list-URLs).
        mailing_list_parse[section] = mailing_list

    # Calculate the total number of lists by iterating through the values of 
    # mailing_list_parse. Note that there are multiple values per key. 
    total_lists = len([item for items in mailing_list_parse.values() 
                                                            for item in items])
    if not total_lists:
        logging.error('No lists found in configuration file')
        sys.exit()
    
    return mailing_list_parse, total_lists


def parse_and_save(mbox_files, nntp=False):
    """Parse the mbox archives to extract the required information.

    Opens each local mbox specified by mbox_files and extracts the required
    information that is then saved to a database.
    """

    # Connect to the database.
    try:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['defaultport'])
    except psycopg2.OperationalError:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['port'])
    cur = conn.cursor()

    current_lists = []
    is_spam = False

    for url, files in mbox_files.iteritems():
        mbox_file = mailbox.mbox(files)
        
        # Name of the mailing list and project.
        mbox_name = os.path.basename(files)
        mailing_list = os.path.basename(files).split('.')[0]
        project = mailing_list.rsplit('-', 2)[0]
        logging.info("Parsing '%s'" % mailing_list)

        for key, message in mbox_file.iteritems():
            # The 'From' field value returns a string of the format:
            #   email-address (Name)
            # from which the sender's name and email address is extracted. Note
            # that this is not considered as SPAM because if the 'From' header
            # is missing, it doesn't make sense to process other headers.
            from_field = message['From']
            if from_field is None:
                continue

            # The Message-ID that can is used to check for errors.
            msg_id_raw = message['Message-ID']
            if msg_id_raw is None:
                logging.warning('No Message-ID found, setting default ID')
                # Create a Message-ID:
                #   sha1(archive_date + project) @ teammetrics-spam.debian.org.
                domain_str = '@teammetrics-spam.debian.org'
                hash_obj = hashlib.sha1()
                hash_string = str(archive_date) + project
                hash_obj.update(hash_string)
                msg_id = hash_obj.hexdigest() + '@teammetrics-spam.debian.org'
                logging.info(debug_msg)
                is_spam = True
            else:
                is_spam = False
                msg_id = msg_id_raw.strip('<>')

            # Set the debug message.
            debug_msg = ("\tMessage-ID %s of '%s' project in mbox file '%s'" %
                                                (msg_id, project, mbox_name))

            # Get the name for two possible cases of formatting of 'From' header.
            #       John Doe <john@doe.com> 
            #       john@doe.com (John Doe)
            if from_field.endswith('>'):
                # Get the position of < and > to parse the email.
                email_start_pos = from_field.find("<")
                email_end_pos = from_field.find(">")
                email_raw = from_field[email_start_pos+1:email_end_pos]
                email_addr = email_raw.replace(' at ', '@')

                name_raw = from_field[:email_start_pos-1].strip()
                name = name_raw.strip("""'"<>""")

            # For the second case.
            elif from_field.endswith(')'):
                # Get the position of ( and ) to parse the name.
                name_start_pos = from_field.find("(")
                name_end_pos = from_field.find(")")
                name_raw = from_field[name_start_pos+1: name_end_pos]
                name = name_raw.strip("""'"<>""")

                email_raw = from_field[:name_start_pos-1]
                email_addr = email_raw.replace(' at ', '@')

            # For no such case, it's better to skip since we need the Name.
            else:
                logging.error("No proper formatting for 'Name' found in %s" % msg_id)
                continue

            # Resolve the encodings but don't skip the message yet; let it
            # go through the SPAM checker.
            try:
                decoded_name = email.header.decode_header(name_raw)
            except ValueError as detail:
                logging.warning("Invalid 'Name' encoding: %s\n%s" % (detail, debug_msg))

            try:
                name = u" ".join([unicode(text, charset or chardet.detect(text)['encoding']) 
                                                            for text, charset in decoded_name])
            except TypeError:
                logging.error("Unable to detect 'Name' encoding for: %s" % msg_id)
                continue
            except (UnicodeDecodeError, LookupError) as detail:
                logging.error("Unable to decode 'Name': %s\n%s" % (detail, debug_msg))

            if name.endswith('alioth.debian.org'):
                name = name.split()[0]

            # The date the message was sent.
            get_date = message['Date']
            parsed_date = email.utils.parsedate(get_date)

            # last_f_date is used in case a message has an invalid date.
            # In such a case, the date of the previous date is used.
            last_f_date = ''

            # Some messages have faulty Date headers. Get the last_f_date in 
            # such cases and even if that fails, skip the message. 
            try:
                format_date = datetime.datetime(*parsed_date[:4])   
            except (ValueError, TypeError) as detail:
                if last_f_date:
                    format_date = last_f_date
                else:
                    logging.error("Invalid 'Date' header: %s\n%s" % (detail, debug_msg))
                    continue
            try:
                archive_date = format_date.strftime("%Y-%m-%d") 
            except ValueError as detail:
                logging.error("Unable to parse 'Date' header: %s\n%s" % (detail, debug_msg))
                continue
            
            try:
                raw_subject = ' '.join(message['Subject'].split())
            except AttributeError as detail:
                logging.error("Invalid 'Subject' header: %s\n%s" % (detail, debug_msg))
                raw_subject = ''

            try:
                decoded_subject = email.header.decode_header(raw_subject)
            except ValueError as detail:
                logging.warning("Invalid 'Subject' encoding: %s" % detail)
            except email.errors.HeaderParseError as detail:
                logging.warning("Unable to parse 'Subject' header: %s\n%s" % (detail, debug_msg))

            try:
                subject = u" ".join([unicode(text, charset or chardet.detect(text)['encoding'])
                                                        for text, charset in decoded_subject])
            except (LookupError, TypeError) as detail:
                logging.error("Unable to detect 'Subject' encoding for %s: %s" % (msg_id, detail))
                continue
            except (UnicodeDecodeError, LookupError) as detail:
                logging.warning("Unable to decode 'Subject': %s\n%s" % (detail, debug_msg))

            # Get the message payload.
            if message.is_multipart():
                # We are interested only in the plain text parts.
                msg_text_parts = [part for part in email.Iterators.typed_subpart_iterator(message,
                                                                                        'text',
                                                                                        'plain')]
                msg_body = []
                for part in msg_text_parts:
                    try:
                        msg_body.append(unicode(part.get_payload(decode=True),
                                                chardet.detect(part.get_payload())['encoding'],
                                                "replace"))
                    except (LookupError, TypeError) as detail:
                        logging.error("Unable to detect payload encoding for %s: %s" % (msg_id, detail))
                        continue
                payload = u"\n".join(msg_body).strip()
            else:
                try:
                    payload = unicode(message.get_payload(decode=True), 
                                      chardet.detect(message.get_payload())['encoding'],
                                      "replace")
                except (LookupError, TypeError) as detail:
                    logging.error("Unable to detect payload encoding for %s: %s" % (msg_id, detail))
                    continue

            is_spam_filter = False
            name, subject, reason, spam = spamfilter.check_spam(name, subject)
            # If the message is spam, set the is_spam_filter flag.
            if is_spam:
                reason = 'No Message-ID found'
            if spam:
                is_spam_filter = True
                logging.warning('Spam detected for %s. Reason: %s' % (msg_id, reason))

            today_raw = datetime.date.today()
            today_date = today_raw.strftime("%Y-%m-%d")

            # The lines in the message body excluding blank lines. 
            msg_blank_raw = [line.strip() for line in payload.splitlines() if line]
            msg_blank = [line for line in msg_blank_raw if line]
            msg_blank_len = len(msg_blank)
            # The lines in the message body excluding blank lines AND
            # quotes (starting with >).
            msg_quotes = [line for line in msg_blank if not line.startswith('>')]
            msg_quotes_len = len(msg_quotes)

            # The number of characters in the message body.
            msg_raw_len = len(''.join(element for element in msg_blank))

            # The lines in the message body excluding blank lines AND
            # quotes and till the signature (-- ).
            try:
                msg_sig_len = len(msg_quotes[:msg_quotes.index('--')])
            except ValueError:
                msg_sig_len = msg_blank_len

            # The netloc from the mailing list URL.
            netloc = urlparse.urlparse(url).netloc

            # Save the required information to the database.
            try:
                cur.execute(
                """INSERT INTO listarchives
                (project, domain, name, email_addr, subject, message_id, archive_date, 
        today_date, msg_raw_len, msg_no_blank_len, msg_no_quotes_len, msg_no_sig_len, is_spam)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                (project, netloc, name, email_addr, subject, msg_id, archive_date, 
        today_date, msg_raw_len, msg_blank_len, msg_quotes_len, msg_sig_len, is_spam_filter)
                            )
            except psycopg2.DataError as detail:
                conn.rollback()
                logging.error(detail)
                logging.error(debug_msg)
                continue
            except psycopg2.IntegrityError as detail:
                # It happens that the very same message hits a mailing list twice
                # for instance because concerning two different bugs and BTS is
                # sending a copy for each bug separately.
                conn.rollback()
                logging.info('Message-ID %s already in database, skipping' % msg_id)
                continue
            conn.commit()
            # Save the date for later use.
            last_f_date = format_date

        current_lists.append(mbox_name)

    logging.info('Updating names')
    updatenames.update_names(conn, cur)

    cur.close()
    conn.close()

    # nntp is True when parse_and_save is saved is being called by nntpstat.
    if not nntp:
        # Write the checksums of the download mbox archives.
        if current_lists:
            write_parsed_lists(current_lists)

        # Remove the extracted mbox archives (in plain text).
        logging.info('Cleaning up extracted mbox archives')
        for each_mbox in mbox_files.itervalues():
            os.remove(each_mbox)

        logging.info('Quit')
        sys.exit()


def main(conf_info, total_lists): 
    """Fetch the mbox archives from the URLs specified.

        mbox_files      -   mapping of URLs to the path of local mbox archives
                            (in plain text format)
        conf_info       -   mapping of list names to their URLs
        mbox_archives   -   mbox archives in gzip format 
    """ 

    count = 0
    mbox_files = {}
    mbox_archives = []
    parsed_lists = get_parsed_lists()
    current_month = get_current_month()

    # The conf_info has a mapping of {list-name : [list-url]}. So we go through
    # each value and download the corresponding list.
    for names, lists in conf_info.iteritems():
        for lst in lists:
            logging.info('\tList %d of %d' % (count+1, total_lists))
            logging.info("Reading %s" % lst)
            try:
                url = urllib2.urlopen(lst)
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
            logging.info("Fetching %d mbox archives:" % len(archive_dates))
            for date in archive_dates:
                # Get the mbox URL and the name. 
                mbox_url = '{0}/{1}'.format(lst, date)
                mbox_name = '{0}-{1}'.format(lst.split('/')[-1], date)

                # If the mbox has already been parsed and is present, then skip.
                # Strip the .gz from the name to match parsed_lists.
                mbox_name_raw = mbox_name.strip('.gz')
                if mbox_name_raw in parsed_lists:
                    logging.warning("Skipping already downloaded "
                                       "and parsed mbox %s" % mbox_name)
                    continue

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
            
                # Extract the mbox file (plain text) from the gzip archive. 
                mbox_plain_text = '{0}'.format(mbox_name.rsplit('.', 1)[0])
                mbox_path = os.path.join(ARCHIVES_FILE_PATH, mbox_plain_text)
                with open(mbox_path, 'w') as gzip_file:
                    archive_contents = gzip.open(path_to_archive, 'rb').read()
                    gzip_file.write(archive_contents)
                    # Update the path to the local mbox file.
                    mbox_files[mbox_url] = mbox_path
                    logging.info('\t%s' % mbox_name)

            count += 1

    # We don't need the mbox archives (gzipped), so delete them.
    if mbox_archives:
        logging.info('Cleaning up downloaded mbox archives')
        for archives in mbox_archives:
            os.remove(archives)

    # If nothing to parse, quit.
    if not mbox_files:
        logging.info('Quit: nothing to parse')
        sys.exit()

    # Open each local mbox archive and then parse it.
    parse_and_save(mbox_files)


def day_of_month_check():
    """Checks for the day of the month.

    Quit if it is the first day of the month else continue for any other day.
    This is to handle the definition of first day safely according to different
    time zones because we do not download mbox archives for the current month.
    """

    today_date = datetime.date.today()
    first_day = datetime.date(today_date.year, today_date.month, 1)
    if today_date == first_day:
        logging.error('Today is the first day of the month')
        logging.error('Please run the script tomorrow')
        sys.exit(1)
    else:
        return 


def start_logging(filename=LOG_FILE_PATH):
    """Initialize the logging."""
    logging.basicConfig(filename,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


if __name__ == '__main__':
    # Create the directories on first run. NOTE: This will be changed later. 
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)
    if not os.path.isfile(LOG_FILE_PATH):
        open(LOG_FILE_PATH, 'w').close()

    # Initialize the logging.
    start_logging()
    logging.info('\t\tStarting ListStat')
    
    # Check which day of the month it is.
    day_of_month_check()

    # Check whether the DATABASE dictionary is populated.
    if not DATABASE['name']:
        logging.error("Please set a value for 'name' key of DATABASE")
        sys.exit(1)

    # Simulate a connection just to check whether everything is OK.
    try:
        conn = psycopg2.connect(database=DATABASE['name'], port=DATABASE['defaultport'])
    except psycopg2.OperationalError:
        try:
            psycopg2.connect(database=DATABASE['name'], port=DATABASE['port'])
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

    # Get the configuration.
    conf_info, total_lists = get_configuration()
    
    main(conf_info, total_lists)
