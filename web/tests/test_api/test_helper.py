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

    def test_processMonthData(self):
        cdata = commitlines.monthData('teammetrics')
        pdata = helper.processMonthData(cdata, ['lines_inserted', 'lines_removed'])
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
        cdata = commitstat.monthData('teammetrics')
        pdata = helper.processMonthData(cdata,['commits'])
        self.assertRaises(IndexError)

    def test_processMonthTopNData(self):
        cdata = commitlines.monthTopN('teammetrics',5)
        pdata = helper.processMonthTopNData(cdata, ['lines_inserted', 'lines_removed'])
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
        cdata = commitstat.monthTopN('teammetrics',5)
        pdata = helper.processMonthTopNData(cdata,['commits'])
        self.assertRaises(IndexError)

    def test_processAnnualData(self):
        cdata = commitlines.annualData('teammetrics')
        pdata = helper.processAnnualData(cdata, ['lines_inserted', 'lines_removed'])
        self.assertTrue(pdata.has_key('annualdata'))
        self.assertIsInstance(pdata['annualdata'],list)
        self.assertTrue(len(pdata['annualdata'])>0)
        self.assertIsInstance(pdata['annualdata'][0],dict)
        self.assertTrue(pdata['annualdata'][0].has_key('lines_inserted'))
        self.assertTrue(pdata['annualdata'][0].has_key('lines_removed'))
        self.assertTrue(pdata['annualdata'][0].has_key('year'))
        cdata = commitstat.annualData('teammetrics')
        pdata = helper.processAnnualData(cdata,['commits'])
        self.assertRaises(IndexError)

    def test_processMonthTopNData(self):
        cdata = commitlines.annualTopN('teammetrics',5)
        pdata = helper.processAnnualTopNData(cdata, ['lines_inserted', 'lines_removed'])
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
        cdata = commitstat.annualTopN('teammetrics',5)
        pdata = helper.processAnnualTopNData(cdata,['commits'])
        self.assertRaises(IndexError)

    def test_monthList(self):
        pdata = helper.monthList('teammetrics', 'teammetrics-discuss')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_monthCommits(self):
        pdata = helper.monthCommits('teammetrics', 'teammetrics')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthCommitLines(self):
        pdata = helper.monthCommitLines('teammetrics', 'teammetrics')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthTopNList(self):
        pdata = helper.monthTopNList('teammetrics', 'teammetrics-discuss', 2)
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_monthTopNCommits(self):
        pdata = helper.monthTopNCommits('teammetrics', 'teammetrics', 2)
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_monthTopNCommitLines(self):
        pdata = helper.monthTopNCommitLines('teammetrics', 'teammetrics', 2)
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualList(self):
        pdata = helper.annualList('teammetrics', 'teammetrics-discuss')
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_annualCommits(self):
        pdata = helper.annualCommits('teammetrics', 'teammetrics')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualCommitLines(self):
        pdata = helper.annualCommitLines('teammetrics', 'teammetrics')
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualTopNList(self):
        pdata = helper.annualTopNList('teammetrics', 'teammetrics-discuss', 2)
        self.assertTrue(pdata.has_key('mailing-list'))
        self.assertEqual(pdata['mailing-list'],'teammetrics-discuss')

    def test_annualTopNCommits(self):
        pdata = helper.annualTopNCommits('teammetrics', 'teammetrics', 2)
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_annualTopNCommitLines(self):
        pdata = helper.annualTopNCommitLines('teammetrics', 'teammetrics', 2)
        self.assertTrue(pdata.has_key('repository'))
        self.assertEqual(pdata['repository'],'teammetrics')

    def test_getMonthData(self):
        cdata = helper.getMonthData('teammetrics','list')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getMonthData('teammetrics','commits')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getMonthData('teammetrics','commitlines')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getMonthTopNData(self):
        cdata = helper.getMonthTopNData('teammetrics','list', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getMonthTopNData('teammetrics','commits', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getMonthTopNData('teammetrics','commitlines', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getAnnualData(self):
        cdata = helper.getAnnualData('teammetrics','list')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getAnnualData('teammetrics','commits')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getAnnualData('teammetrics','commitlines')
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)

    def test_getAnnualTopNData(self):
        cdata = helper.getAnnualTopNData('teammetrics','list', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'list')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getAnnualTopNData('teammetrics','commits', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commits')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
        cdata = helper.getAnnualTopNData('teammetrics','commitlines', 2)
        self.assertIsInstance(cdata,dict)
        self.assertTrue(cdata.has_key('metric'))
        self.assertEqual(cdata['metric'],'commitlines')
        self.assertTrue(cdata.has_key('data'))
        self.assertIsInstance(cdata['data'], list)
