import logging
logging.basicConfig()
def get(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
