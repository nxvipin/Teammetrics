from web.api import helper, settings
from web.models import commitlines, commitstat, listarchives
from web.lib import log
import unittest

logger = log.get(__name__)

class HelperTest(unittest.TestCase):

    def test_checkKeyValueExist(self):
        cdata = [{"year":1},{"year":2}]
        self.assertTrue(helper.checkKeyValueExist(cdata,'year',2)>=0)
        self.assertTrue(helper.checkKeyValueExist(cdata,'year',0)==-1)
        self.assertTrue(helper.checkKeyValueExist(cdata,'RandomKey',5)==-1)

    def test_keyValueIndex(self):
        cdata = [{"year":1},{"year":2}]
        self.assertEqual(helper.keyValueIndex(cdata,'year',2),1)
        self.assertEqual(helper.keyValueIndex(cdata,'NewKey',100),2)

    def test_processData(self):
        cdata = commitlines.get('teammetrics', n=None, datascale='month')
        pdata = helper.processData(cdata, ['lines_inserted', 'lines_removed'], n=None, datascale='month')
        self.assertTrue(pdata.has_key('annualdata'))
        self.assertIsInstance(pdata['annualdata'],list)
        self.assertTrue(len(pdata['annualdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0].has_key('monthlydata'))
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'],list)
        self.assertTrue(len(pdata['annualdata'][0]['monthlydata'])>0)
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'][0],dict)
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0].has_key('lines_inserted'))
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0].has_key('lines_removed'))
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0].has_key('month'))
        cdata = commitstat.get('teammetrics', n=None, datascale='month')
        pdata = helper.processData(cdata,['commits'], n=None, datascale='month')
        self.assertRaises(IndexError)

    def test_processMonthTopNData(self):
        cdata = commitlines.get('teammetrics', n=5, datascale='month')
        pdata = helper.processData(cdata, ['lines_inserted', 'lines_removed'], n=5, datascale='month')
        self.assertTrue(pdata.has_key('annualdata'))
        self.assertIsInstance(pdata['annualdata'],list)
        self.assertTrue(len(pdata['annualdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0].has_key('monthlydata'))
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'],list)
        self.assertTrue(len(pdata['annualdata'][0]['monthlydata'])>0)
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'][0],dict)
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0].has_key('userdata'))
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0].has_key('month'))
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'][0]['userdata'],list)
        self.assertTrue(len(pdata['annualdata'][0]['monthlydata'][0]['userdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0]['monthlydata'][0]['userdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0]['userdata'][0].has_key('name'))
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0]['userdata'][0].has_key('lines_inserted'))
        self.assertTrue(pdata['annualdata'][0]['monthlydata'][0]['userdata'][0].has_key('lines_removed'))
        cdata = commitstat.get('teammetrics', n=5, datascale='month')
        pdata = helper.processData(cdata, ['commits'], n=5, datascale='month')
        self.assertRaises(IndexError)

    def test_processAnnualData(self):
        cdata = commitlines.get('teammetrics', n=None, datascale='annual')
        pdata = helper.processData(cdata, ['lines_inserted', 'lines_removed'], n=None, datascale='annual')
        self.assertTrue(pdata.has_key('annualdata'))
        self.assertIsInstance(pdata['annualdata'],list)
        self.assertTrue(len(pdata['annualdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0].has_key('lines_inserted'))
        self.assertTrue(pdata['annualdata'][0].has_key('lines_removed'))
        self.assertTrue(pdata['annualdata'][0].has_key('year'))
        cdata = commitstat.get('teammetrics', n=None, datascale='annual')
        pdata = helper.processData(cdata, ['commits'], n=None, datascale='annual')
        self.assertRaises(IndexError)

    def test_processAnnualTopNData(self):
        cdata = commitlines.get('teammetrics', n=5, datascale='annual')
        pdata = helper.processData(cdata, ['lines_inserted', 'lines_removed'], n=5, datascale='annual')
        self.assertTrue(pdata.has_key('annualdata'))
        self.assertIsInstance(pdata['annualdata'],list)
        self.assertTrue(len(pdata['annualdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0].has_key('userdata'))
        self.assertTrue(pdata['annualdata'][0].has_key('year'))
        self.assertIsInstance(pdata['annualdata'][0]['userdata'],list)
        self.assertTrue(len(pdata['annualdata'][0]['userdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0]['userdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0]['userdata'][0].has_key('name'))
        self.assertTrue(pdata['annualdata'][0]['userdata'][0].has_key('lines_inserted'))
        self.assertTrue(pdata['annualdata'][0]['userdata'][0].has_key('lines_removed'))
        cdata = commitstat.get('teammetrics', n=5, datascale='annual')
        pdata = helper.processData(cdata, ['commits'], n=5, datascale='annual')
        self.assertRaises(IndexError)

    def test_monthList(self):
        pdata = helper.List('teammetrics-discuss', n=None, datascale='month')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_monthCommits(self):
        pdata = helper.Commits('teammetrics', n=None, datascale='month')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthCommitLines(self):
        pdata = helper.Commitlines('teammetrics', n=None, datascale='month')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthTopNList(self):
        pdata = helper.List('teammetrics-discuss', n=5, datascale='month')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_monthTopNCommits(self):
        pdata = helper.Commits('teammetrics', n=5, datascale='month')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthTopNCommitLines(self):
        pdata = helper.Commitlines('teammetrics', n=5, datascale='month')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualList(self):
        pdata = helper.List('teammetrics-discuss', n=None, datascale='annual')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_annualCommits(self):
        pdata = helper.Commits('teammetrics', n=None, datascale='annual')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualCommitLines(self):
        pdata = helper.Commitlines('teammetrics', n=None, datascale='annual')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualTopNList(self):
        pdata = helper.List('teammetrics-discuss', n=5, datascale='annual')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_annualTopNCommits(self):
        pdata = helper.Commits('teammetrics', n=5, datascale='annual')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualTopNCommitLines(self):
        pdata = helper.Commitlines('teammetrics', n=5, datascale='annual')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_getMonthData(self):
        cdata = helper.getData('teammetrics','list',n=None, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commits',n=None, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commitlines',n=None, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getMonthTopNData(self):
        cdata = helper.getData('teammetrics','list',n=2, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commits',n=2, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commitlines',n=2, datascale='month')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getAnnualData(self):
        cdata = helper.getData('teammetrics','list',n=None, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commits',n=None, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commitlines',n=None, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getAnnualTopNData(self):
        cdata = helper.getData('teammetrics','list',n=2, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commits',n=2, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getData('teammetrics','commitlines',n=2, datascale='annual')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
