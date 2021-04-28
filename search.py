import sqlite3
import sys
import argparse
import time
import json
import os
from geo import Geo
from kdsearch import get_neighbors


class Extractor:
    def __init__(self, name_db):
        try:
            os.chdir('db')
            if os.path.exists(name_db):
                self.conn = sqlite3.connect(name_db)
                self.cursor = self.conn.cursor()
            else:
                raise Exception()
        except Exception:
            print('Не удалось подключиться к базе данных', file=sys.stderr)
            sys.exit(1)

    def get_cities_list(self):
        self.cursor.execute('''SELECT * FROM cities''')
        return self.cursor.fetchall()

    def get_streets_list(self, name_table):
        self.cursor.execute(
            '''SELECT street FROM "{0}"'''.format(name_table))
        return self.cursor.fetchall()

    def get_buildings_list(self, name_table, street, housenumber):
        self.cursor.execute(
            '''SELECT * FROM "{0}" WHERE street=? AND housenumber=?'''
            .format(name_table), (street, housenumber,))
        return self.cursor.fetchall()

    def kill(self):
        self.conn.commit()
        self.conn.close()


class Searcher:
    @staticmethod
    def search(args):
        extractor = Extractor(args.name_db)
        geo = Geo(*(InfoGetter.get_info(
            args.address.replace(',', ' ').split(), extractor)))
        if geo is None:
            Searcher.print_not_found_message(args.address)

        correct_address = f'{geo.city} {geo.streettype} ' \
                          f'{geo.street} {geo.housenumber}'
        ld = get_levenshtein_distance(args.address, correct_address)

        if args.nc and ld != 0:
            Searcher.print_not_found_message(args.address)
        if not args.nv and ld != 0:
            print(f'Возможно Вы имели в виду: {correct_address}')
        if args.r != 0:
            neighbors = get_neighbors(geo, args.r)
            for neighbor in neighbors:
                Searcher.print_info(neighbor[1], neighbor[0])
        else:
            Searcher.print_info(geo)
        extractor.kill()

    @staticmethod
    def print_info(geo, distance=0):
        res_dict = {
            "address": {
                "addr:country": "Россия",
                "addr:region": geo.region,
                "addr:city": geo.city,
                "addr:street": geo.street,
                "addr:streettype": geo.streettype,
                "addr:housenumber": geo.housenumber
            },
            "coordinates": {
                "lat": geo.lat,
                "lon": geo.lon
            }
        }
        if distance != 0:
            res_dict["distance"] = {"meters": round(distance)}
        res_json = json.dumps(res_dict, indent=2, ensure_ascii=False)
        print(res_json)

    @staticmethod
    def print_not_found_message(address):
        print('{0} не найден'.format(address))
        sys.exit(2)


class InfoGetter:
    @staticmethod
    def get_info(address, extractor):
        city_info = InfoGetter.get_city_info(
            address, extractor.get_cities_list())
        if city_info is None:
            return None
        streettype = InfoGetter.get_streettype(address)
        housenumber = InfoGetter.get_housenumber(address)
        street = InfoGetter.get_street(
            address, extractor.get_streets_list(city_info[2]))
        if street is None:
            return None
        building_info = InfoGetter.get_building_info(
            extractor.get_buildings_list(city_info[2], street, housenumber),
            streettype)
        if building_info is None:
            return None
        return city_info, building_info

    @staticmethod
    def get_city_info(address, cities_list):
        for i in range(len(address)):
            city_name = ' '.join(address[0:i+1])
            city_info = min(
                cities_list,
                key=lambda city: get_levenshtein_distance(
                    city[0], city_name))
            if (get_levenshtein_distance(
                    city_name, city_info[0]) <= len(city_name) / 3):
                del address[0:i+1]
                return city_info
        return None

    @staticmethod
    def get_streettype(address):
        abbr_dict = {
            "улица": ["улица", "у", "ул"],
            "проспект": ["проспект", "прт", "пр", "пр-т"],
            "километр": ["километр", "км"],
            "переулок": ["переулок", "пер", "переул"],
            "станция": ["станция", "ст"],
            "шоссе": ["шоссе", "ш"]
        }
        rev_abbr_dict = reverse_dict(abbr_dict)
        possible = address[0].lower().replace('.', '')
        if rev_abbr_dict.get(possible) is not None:
            del address[0]
            return rev_abbr_dict[possible]
        streettype = min(
            abbr_dict.keys(),
            key=lambda abbr: get_levenshtein_distance(
                abbr, possible))
        if (get_levenshtein_distance(
                streettype, possible) <= 2):
            del address[0]
            return streettype
        return '%'

    @staticmethod
    def get_housenumber(address):
        if address[-1].isalpha():
            housenumber = ''.join(address[-2:]).upper()
            del address[-2:]
        else:
            housenumber = address[-1].upper()
            del address[-1]
        return housenumber

    @staticmethod
    def get_street(address, street_list):
        street = ' '.join(address).title()
        possible_street = min(
            set(street_list),
            key=lambda str: get_levenshtein_distance(
                str[0], street))[0]
        if (get_levenshtein_distance(possible_street, street)
                <= len(street) / 3):
            return possible_street
        return None

    @staticmethod
    def get_building_info(building_list, streettype):
        if len(building_list) == 0:
            return None
        for building in building_list:
            if building[1] == streettype:
                return building
        return building_list[0]


def get_levenshtein_distance(word1, word2):
    len1 = len(word1)
    len2 = len(word2)
    current_line = []
    for i in range(len2 + 1):
        current_line.append(i)
    for i in range(len1):
        previous_line = current_line.copy()
        current_line[0] = previous_line[0] + 1
        for j in range(len2):
            if word1[i] == word2[j]:
                current_line[j + 1] = previous_line[j]
                continue
            current_line[j + 1] = 1 + min(previous_line[j],
                                          previous_line[j + 1],
                                          current_line[j])
    return current_line[len2]


def reverse_dict(dict):
    new_dict = {}
    for item in dict.items():
        for value in item[1]:
            new_dict[value] = item[0]
    return new_dict


def get_args_parser():
    arg_parser = argparse.ArgumentParser(
        description='Получение адресов и координат')
    arg_parser.add_argument('name_db', type=str, help='имя базы данных')
    arg_parser.add_argument('address', type=str,
                            help='адрес желаемого здания')
    arg_parser.add_argument('--nv', '--no-verbose',
                            action='store_true', dest='nv',
                            help='вывод без информации об исправлении ошибок')
    arg_parser.add_argument('--nc', '--no-corrected',
                            action='store_true', dest='nc',
                            help='режим без исправления ошибок')
    arg_parser.add_argument('-r', action='store', dest='r',
                            type=int, help='радиус поиска', default=0)
    return arg_parser


if __name__ == '__main__':
    start_time = time.time()
    args_parser = get_args_parser()
    args = args_parser.parse_args()
    Searcher.search(args)
    print('{0:.3f} seconds'.format(time.time() - start_time), file=sys.stderr)
