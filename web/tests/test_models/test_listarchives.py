from web.models import listarchives
import unittest

class ListArchivesTest(unittest.TestCase):
    def setUp(self):
        #Correct Monthly Data
        self.cmdata = listarchives.monthData('teammetrics-discuss')
        #Correct Monthly Data for Top 'N' Contributors
        self.cmdataN = listarchives.monthTopN('teammetrics-discuss', 5)
        #Correct Annual Data
        self.cadata = listarchives.annualData('teammetrics-discuss')
        #Correct Annual Data for Top 'N' Contributors
        self.cadataN = listarchives.annualTopN('teammetrics-discuss', 5)
        #Incorrect Monthly Data
        self.imdata = listarchives.monthData('SomeRandomNameNotInDatabase')
        #Incorrect Monthly Data for Top 'N' Contributors
        self.imdataN = listarchives.monthTopN('SomeRandomNameNotInDatabase', 5)
        #Incorrect Annual Data
        self.iadata = listarchives.annualData('SomeRandomNameNotInDatabase')
        #Incorrect Annual Data for Top 'N' Contributors
        self.iadataN = listarchives.annualTopN('SomeRandomNameNotInDatabase', 5)

    def test_correctMonthData(self):
        self.assertEqual(type(self.cmdata),list)
        self.assertTrue(len(self.cmdata)>0)
        for unit in self.cmdata:
            self.assertEqual(len(unit),3)

    def test_correctMonthTopN(self):
        self.assertEqual(type(self.cmdataN),list)
        self.assertTrue(len(self.cmdataN)>0)
        for unit in self.cmdataN:
            self.assertEqual(len(unit),4)

    def test_correctAnnualData(self):
        self.assertEqual(type(self.cadata),list)
        self.assertTrue(len(self.cadata)>0)
        for unit in self.cadata:
            self.assertEqual(len(unit),2)

    def test_correctAnnualTopN(self):
        self.assertEqual(type(self.cadataN),list)
        self.assertTrue(len(self.cadataN)>0)
        for unit in self.cadataN:
            self.assertEqual(len(unit),3)

    def test_incorrectData(self):
        self.assertEqual(type(self.imdata),list)
        self.assertEqual(len(self.imdata),0)
        self.assertEqual(type(self.imdataN),list)
        self.assertEqual(len(self.imdataN),0)
        self.assertEqual(type(self.iadata),list)
        self.assertEqual(len(self.iadata),0)
        self.assertEqual(type(self.iadataN),list)
        self.assertEqual(len(self.iadataN),0)

