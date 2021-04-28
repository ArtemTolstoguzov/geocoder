import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from pretreatment import preprocessor as pp


class ArgsParserTest(unittest.TestCase):
    def test_args_parser_getter(self):
        args_parser = pp.get_args_parser()
        self.assertIsNotNone(args_parser)


class OverpassApiGetterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.getter = pp.OverpassApiGetter()

    def test_correct_getter(self):
        self.assertIsNotNone(self.getter)

    def test_xml_ways(self):
        codes = ['1775054', '1663622']
        for code in codes:
            xml = self.getter.get_xml_ways(code)
            self.assertIsNotNone(xml)

    def test_get_iter_ways_with_not_empty_xml(self):
        iter_ = pp.get_iter_ways(self.getter.get_xml_ways(3437213))
        self.assertIsNotNone(iter_)

    def test_get_iter_ways_with_empty_xml(self):
        iter_ = pp.get_iter_ways(self.getter.get_xml_ways(2555060))
        self.assertIsNone(iter_)


class DumperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dumper = pp.Dumper('test.db')
        getter = pp.OverpassApiGetter()
        iter_ = pp.get_iter_ways(getter.get_xml_ways(2378241))
        cls.dumper.dump_city('Свердловская область', 'Атиг', 2378241, iter_)

    @classmethod
    def tearDownClass(cls):
        cls.dumper.kill()
        os.remove('../test.db')

    def test_creature_db(self):
        self.dumper.cursor.execute(
            """SELECT name FROM sqlite_master
             WHERE type="table" AND name=\"cities\"""")
        row = self.dumper.cursor.fetchall()
        self.assertEqual(row[0][0], 'cities')

    def test_add_city_in_cities(self):
        self.dumper.cursor.execute(
            """SELECT region, name_table FROM cities WHERE city=\"Атиг\"""")
        row = self.dumper.cursor.fetchall()
        self.assertIsNotNone(row)

    def test_creature_city_table(self):
        self.dumper.cursor.execute(
            """SELECT name FROM sqlite_master
             WHERE type="table" AND name=\"2378241\"""")
        row = self.dumper.cursor.fetchall()
        self.assertEqual(row[0][0], '2378241')

    def test_city_table_is_not_empty(self):
        self.dumper.cursor.execute(
            """SELECT * FROM \"2378241\"""")
        row = self.dumper.cursor.fetchall()
        self.assertIsNotNone(row)


class CorrectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corrector = pp.AddressSpliter()

    def test_get_street_and_streettype(self):
        streets = ['улица Ленина', 'проспект Малышева', 'переулок Цветочный',
                   'Цветочная улица', 'Ленинградский проспект', 'ЕКАД',
                   'Академический м-н', '7 км', 'Восточная станция',
                   'Большой пр-т']
        res = []
        correct_streets = [['улица', 'Ленина'], ['проспект', 'Малышева'],
                           ['переулок', 'Цветочный'], ('улица', 'Цветочная'),
                           ('проспект', 'Ленинградский'), ('-', 'ЕКАД'),
                           ('микрорайон', 'Академический'), ('километр', '7'),
                           ('станция', 'Восточная'), ('проспект', 'Большой')]

        for street in streets:
            res.append(
                self.corrector.get_street_and_streettype(street))
        self.assertListEqual(correct_streets, res)


if __name__ == '__main__':
    unittest.main()
