#! /usr/bin/env python

"""Fetches and parses web archives from lists.debian.org."""

import re
import urllib2
import logging

from BeautifulSoup import BeautifulSoup

import liststat

BASE_URL = 'http://lists.debian.org/'


def main():
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
                    all_elements_text = [element.text for element in all_elements]

            counter += 1


if __name__ == '__main__':
    liststat.start_logging()
    logging.info('\t\tStarting Web Archive Parser')

    main()
