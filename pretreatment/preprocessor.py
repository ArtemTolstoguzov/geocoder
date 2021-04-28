from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import HTTPError
import re
import sqlite3
import argparse
import hashlib
import time


class AddressSpliter:
    def __init__(self):
        self.split_street_pattern = re.compile(r'(.+?) (гавань|слобода|'
                                               r'коса|роща|поселение|'
                                               r'шоссе|парк|территория|'
                                               r'лесничество|улица|кольцо|'
                                               r'просек|берег|набережная|'
                                               r'пансионат|вал|проспект|'
                                               r'км|поле|канал|платформа|'
                                               r'дорожка|двор|бульвар|м-н|'
                                               r'село|пр-т|сад|проток|'
                                               r'аэропорт|дорога|островок|'
                                               r'километр|микрорайон|'
                                               r'остров|аллея|проезд|'
                                               r'квартал|товарищество|'
                                               r'линия|станция|тупик|'
                                               r'площадь|городок|пост|'
                                               r'переулок|тракт)')

    def get_street_and_streettype(self, street):
        split_street = self.split_street_pattern.search(street)
        type_and_name = street.split(' ', 1)
        if split_street is None:
            if len(type_and_name) != 2:
                return '-', street
            return type_and_name
        if split_street[2] == 'пр-т':
            return 'проспект', split_street[1]
        if split_street[2] == 'км':
            return 'километр', split_street[1]
        if split_street[2] == 'м-н':
            return 'микрорайон', split_street[1]
        return split_street[2], split_street[1]


class Dumper:
    def __init__(self, name_db):
        self.conn = sqlite3.connect('../{0}'.format(name_db))
        self.cursor = self.conn.cursor()
        self.spliter = AddressSpliter()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS
            cities (city text, region text, name_table text)""")

    def dump_city(self, region, name, code, way_iter):
        self.cursor.execute(
            """INSERT OR IGNORE INTO cities VALUES ("{0}", "{1}", "{2}")"""
            .format(name, region, code))
        self.cursor.execute(
            """CREATE TABLE "{0}"
             (hash text, streettype text, street text, housenumber text,
             lat float, lon float, UNIQUE (hash))""" .format(code))
        print(name)
        for way in way_iter:
            street_info = self.spliter.get_street_and_streettype(way[4])
            address = \
                '{0} {1} {2}'.format(street_info[0], street_info[1], way[3])
            hash_ = hashlib.md5(address.encode('utf-8'))
            self.cursor.execute(
                """INSERT OR IGNORE INTO "{0}" VALUES
                ("{1}", "{2}", "{3}", "{4}", "{5}", "{6}")"""
                .format(
                    code, hash_.hexdigest(), street_info[0], street_info[1],
                    way[3], way[1], way[2]))
        self.conn.commit()

    def kill(self):
        self.conn.commit()
        self.conn.close()


class OverpassApiGetter:
    def __init__(self):
        self.overpass_api = 'http://overpass-api.de/api/interpreter?data='

    def get_xml_ways(self, code):
        query = quote(r'[out:xml][timeout:360];area({0});'
                      r'way["building"!="no"]'
                      r'["addr:housenumber"]'
                      r'["addr:street"](area);'
                      r'out center;'.format(3600000000 + int(code)))
        with urlopen(self.overpass_api + query) as page:
            content = page.read().decode('utf-8', errors='ignore')
            return content


def get_iter_ways(xml):
    way_pattern = re.compile(r'<way.+?'
                             r'<center lat="(.+?)" lon="(.+?)".+?'
                             r'<tag k="addr:housenumber" v="(.+?)".+?'
                             r'<tag k="addr:street" v="(.+?)"/>',
                             flags=re.DOTALL)
    if xml.find('<way') == -1:
        return None
    return way_pattern.finditer(xml)


def get_args_parser():
    arg_parser = argparse.ArgumentParser(description='Write in DB')
    arg_parser.add_argument('cities_path',
                            type=str,
                            help='path to cities list in txt-format')
    arg_parser.add_argument('name_db', type=str, help='name of DB')
    return arg_parser


if __name__ == '__main__':
    args_parser = get_args_parser()
    args = args_parser.parse_args()

    overpass_api_getter = OverpassApiGetter()
    dumper = Dumper(args.name_db)

    with open(args.cities_path, 'r', encoding='utf-8') as cities:
        for city in cities:
            city_info = city.split(',')
            xml_ways = overpass_api_getter.get_xml_ways(city_info[1])
            iter_ways = get_iter_ways(xml_ways)
            if iter_ways is None:
                continue
            dumper.dump_city(
                city_info[2][:-1],
                city_info[0],
                city_info[1],
                iter_ways)

    dumper.kill()
