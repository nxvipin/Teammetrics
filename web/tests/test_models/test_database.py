from web.models import database
import psycopg2
import unittest

class DatabaseTest(unittest.TestCase):
    def test_connect(self):
        cursor = database.connect()
        self.assertEqual(type(cursor),psycopg2._psycopg.cursor)
