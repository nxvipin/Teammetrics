from web.lib import metrics
import web.settings as settings
import ConfigParser
import unittest

class MetricsTest(unittest.TestCase):

    def test_correctInput(self):
        data = metrics.get('teammetrics','list')
        self.assertIsInstance(data,list)
        self.assertTrue(len(data)>0)
        self.assertIn('teammetrics-discuss', data)

    def test_incorrectInput(self):
        data = metrics.get('teammetrics','blah')
        self.assertEqual(len(data),0)
        data = metrics.get('blah','teammetrics')
        self.assertEqual(len(data),0)
