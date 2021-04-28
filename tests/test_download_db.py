import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
import download_db as ddb


class DumperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ddb.download_db([('https://yadi.sk/d/68mMaIRDXzs0SA', 'test.db')])

    @classmethod
    def tearDownClass(cls):
        os.remove('test.db')

    def test_creature_db(self):
        self.assertNotEqual(0, os.stat('test.db').st_size)


if __name__ == '__main__':
    unittest.main()
