from web.lib import log
import logging
import unittest

class LogTest(unittest.TestCase):
    def setUp(self):
        self.logger = log.get('testlogger')
    def test_logger(self):
        self.assertEqual(self.logger.name,'testlogger')
        self.assertEqual(self.logger.level,logging.DEBUG)
