import ConfigParser
import sys
import os
from web.lib import log
import web.settings as settings

logger = log.get(__name__)

cp = ConfigParser.ConfigParser()

CONF_FILE = settings.CONFIG_FILE['metrics']

try:
    cp.readfp(open(CONF_FILE))
except IOError:
    logger.error("Config File Not Found")
else:
    def get(metricname, listname):
        logger.info("metrics.get called")
        try:
            mlist = cp.get(metricname,listname).split(',')
            mlist = [name.strip() for name in mlist]
        except ConfigParser.NoSectionError:
            logger.error("No Such Team")
            return []
        except ConfigParser.NoOptionError:
            logger.error("No Such Metric")
            return []
        else:
            return mlist

if __name__ == '__main__':
    print get('sampleteam','list')
