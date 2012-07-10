import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'

from django.http import HttpResponse
from django.test.client import RequestFactory
from web.api import settings
from web.lib import lib
import unittest


class LibTest(unittest.TestCase):

    def setUp(self):
        
        def jsontest():
            @lib.jsonify
            def fun():
                return []
            return fun
            
        def versiontest():
            @lib.versionCheck
            def fun(api_version):
                print api_version
                return {}
            return fun
            
        def respondtest():
            @lib.respond()
            def fun():
                return {}
            return fun
            
        def respondjsontest():
            @lib.respond('JSON')
            def fun():
                return {}
            return fun
            
        self.jsontest = jsontest
        self.versiontest = versiontest
        self.respondtest = respondtest
        self.respondjsontest = respondjsontest

    def test_jsonify(self):
        f = self.jsontest()
        res = f()
        self.assertIsInstance(res, str)

    def test_versionCheck(self):
        settings.API_CURRENT_VERSION = 2
        settings.API_SUPPORTED_VERSIONS = [1,2]
        f = self.versiontest()
        res = f(api_version=2)
        self.assertFalse(res.has_key('error'))
        self.assertFalse(res.has_key('warning'))
        self.assertIsInstance(res,dict)
        res = f(api_version=1)
        self.assertIsInstance(res,dict)
        self.assertTrue(res.has_key('warning'))
        res = f(api_version=0)
        self.assertIsInstance(res,dict)
        self.assertTrue(res.has_key('error'))

    def test_respond(self):
        f = self.respondtest()
        res = f()
        self.assertIsInstance(res, HttpResponse)
        self.assertTrue(res.status_code,200)
        self.assertTrue(res.get('Content-Type').startswith('text/html'))
        f = self.respondjsontest()
        res = f()
        self.assertIsInstance(res, HttpResponse)
        self.assertTrue(res.status_code,200)
        self.assertTrue(res.get('Content-Type').startswith('application/json'))

    def test_dateRange(self):
        factory = RequestFactory()
        request = factory.get('/?startyear=2012&startmonth=01&endyear=2014&endmonth=12')
        x = lib.dateRange(request)
        self.assertIsInstance(x,tuple)
        self.assertEqual(len(x),2)
        self.assertEqual(x[0],'2012-01-01')
        self.assertEqual(x[1],'2014-12-01')
        
        request = factory.get('/')
        x = lib.dateRange(request)
        self.assertIsInstance(x,tuple)
        self.assertEqual(len(x),2)
        self.assertEqual(x[0],'epoch')
        self.assertEqual(x[1],'now')
