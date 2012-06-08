import ConfigParser
import sys
import os
import logging
import web.settings as settings

cp = ConfigParser.ConfigParser()

CONF_FILE = settings.CONFIG_FILE['metrics']

try:
    cp.readfp(open(CONF_FILE))
except IOError:
    logging.error("Config File Not Found")
else:
    def get(metricname, listname):
        logging.info("metrics.get called")
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
    print get('sampleteam','list')
