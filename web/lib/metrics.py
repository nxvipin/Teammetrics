import ConfigParser
import sys
import os
import logging

cp = ConfigParser.ConfigParser()

"""
This is a temporary solution.
Config file will be read from Django settings.
"""
FILE = '../config/metrics.conf'
CONF_FILE = os.path.join(os.path.dirname(sys.argv[0]),FILE)

try:
    cp.readfp(open(CONF_FILE))
except IOError:
    logging.error("Config File Not Found")
else:
    def getMetric(metricname, listname):
        try:
            mlist = cp.get(metricname,listname).split(',')
            mlist = [name.strip() for name in mlist]
        except ConfigParser.NoSectionError:
            logging.error("No Such Team")
            return []
        except ConfigParser.NoOptionError:
            logging.error("No Such Metric")
            return []
        else:
            return mlist

if __name__ == '__main__':
    print getMetric('sampleteam','list')
