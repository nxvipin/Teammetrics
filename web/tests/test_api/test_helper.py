from web.api import helper, settings
from web.lib import log
import unittest

logger = log.get(__name__)

class HelperTest(unittest.TestCase):

    def test_identifyMetric(self):
        cdata = helper.identifyMetric('teammetrics','list')
        self.assertIsInstance(cdata,list)
        self.assertTrue(len(cdata)>0)
        self.assertIn('teammetrics-discuss', cdata)
        
        cdata = helper.identifyMetric('teammetrics','commits')
        self.assertIsInstance(cdata,list)
        self.assertTrue(len(cdata)>0)
        self.assertIn('teammetrics', cdata)
        
        idata = helper.identifyMetric('teammetrics','RandomMetric')
        self.assertIsInstance(idata,list)
        self.assertEqual(len(idata), 0)
        
        idata = helper.identifyMetric('RandomName','commitlines')
        self.assertIsInstance(idata,list)
        self.assertEqual(len(idata), 0)
        
        idata = helper.identifyMetric('RandomName','RandomMetric')
        self.assertIsInstance(idata,list)
        self.assertEqual(len(idata), 0)

    def test_version(self):
        self.assertTrue(helper.version(1))
        self.assertFalse(helper.version(0))

    def test_checkKeyValueExist(self):
        cdata = [{"year":1},{"year":2}]
        self.assertTrue(helper.checkKeyValueExist(cdata,'year',2)>=0)
        self.assertTrue(helper.checkKeyValueExist(cdata,'year',0)==-1)
        
