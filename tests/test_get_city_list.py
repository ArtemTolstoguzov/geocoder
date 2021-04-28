import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from pretreatment import get_city_list as gcl


class GetCityListTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cities_xml = gcl.get_cities_xml()

    @classmethod
    def tearDownClass(cls):
        os.remove('cities_from_osm.txt')

    def test_get_cities_xml(self):
        self.assertIsNotNone(self.cities_xml)

    def test_get_cities_iter(self):
        cities_iter = gcl.get_cities_iter(self.cities_xml)
        self.assertIsNotNone(cities_iter)

    def test_write_result_in_txt(self):
        gcl.write_result_in_txt()
        self.assertNotEqual(0, os.stat('cities_from_osm.txt').st_size)


if __name__ == '__main__':
    unittest.main()
