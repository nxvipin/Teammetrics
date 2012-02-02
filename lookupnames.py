#! /usr/bin/env python

import urllib2
import BeautifulSoup

URL = 'https://alioth.debian.org/users/{0}'
OUTPUT = '{0}\t\t\t\t\t:\t\t\t{1}\n'


def main():
    out = open('matchednames.list', 'w')

    total = 0
    failed = 0
    with open('lookupnames.list') as f:
        for line in f:
            soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(URL.format(line.strip())).read())
            try:
                name = soup.find('span', {'property': 'foaf:name'}).renderContents()
                total += 1
            except AttributeError:
                print 'Nothing found for user:', line,
                failed += 1
                continue

            out.write(OUTPUT.format(name, line.strip()))
            out.flush()

    out.close()
    
    print 'Downloaded: {0}, Failed: {1}'.format(total, failed)
    
main()
