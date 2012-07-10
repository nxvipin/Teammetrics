from web.models import commitlines
import unittest

class CommitLinesTest(unittest.TestCase):
    def setUp(self):
        #Correct Monthly Data
        self.cmdata = commitlines.get(team='teammetrics', n=None, datascale='month')
        #Correct Monthly Data for Top 'N' Contributors
        self.cmdataN = commitlines.get(team='teammetrics', n=5, datascale='month')
        #Correct Annual Data
        self.cadata = commitlines.get(team='teammetrics', n=None, datascale='annual')
        #Correct Annual Data for Top 'N' Contributors
        self.cadataN = commitlines.get(team='teammetrics', n=5, datascale='annual')
        #Incorrect Monthly Data
        self.imdata = commitlines.get(team='RandomName', n=None, datascale='month')
        #Incorrect Monthly Data for Top 'N' Contributors
        self.imdataN = commitlines.get(team='RandomName', n=5, datascale='month')
        #Incorrect Annual Data
        self.iadata = commitlines.get(team='RandomName', n=None, datascale='annual')
        #Incorrect Annual Data for Top 'N' Contributors
        self.iadataN = commitlines.get(team='RandomName', n=5, datascale='annual')
        #Incorrect datascale
        self.ids = commitlines.get(team='teammetrics', n=None, datascale='WrongScale')

    def test_correctMonthData(self):
        self.assertEqual(type(self.cmdata),list)
        self.assertTrue(len(self.cmdata)>0)
        for unit in self.cmdata:
            self.assertEqual(len(unit),4)

    def test_correctMonthTopN(self):
        self.assertEqual(type(self.cmdataN),list)
        self.assertTrue(len(self.cmdataN)>0)
        for unit in self.cmdataN:
            self.assertEqual(len(unit),5)

    def test_correctAnnualData(self):
        self.assertEqual(type(self.cadata),list)
        self.assertTrue(len(self.cadata)>0)
        for unit in self.cadata:
            self.assertEqual(len(unit),3)

    def test_correctAnnualTopN(self):
        self.assertEqual(type(self.cadataN),list)
        self.assertTrue(len(self.cadataN)>0)
        for unit in self.cadataN:
            self.assertEqual(len(unit),4)

    def test_incorrectData(self):
        self.assertEqual(type(self.imdata),list)
        self.assertEqual(len(self.imdata),0)
        self.assertEqual(type(self.imdataN),list)
        self.assertEqual(len(self.imdataN),0)
        self.assertEqual(type(self.iadata),list)
        self.assertEqual(len(self.iadata),0)
        self.assertEqual(type(self.iadataN),list)
        self.assertEqual(len(self.iadataN),0)
        self.assertEqual(self.ids,None)

    def test_getTopN(self):
        data = commitlines.getTopN('teammetrics')
        self.assertIsInstance(data,list)
        self.assertTrue(len(data)>0)
        self.assertIsInstance(data[0],tuple)

