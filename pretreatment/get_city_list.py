from urllib.request import urlopen
import re


def get_cities_xml():
    query = "http://overpass-api.de/api/interpreter?data=[out:json];" \
            "rel[%22addr:country%22=%22RU%22]" \
            "[%22place%22~%22town|city|suburb|hamlet|village%22];out;"

    with urlopen(query) as page:
        content = page.read().decode('utf-8', errors='ignore')
        return content


def get_cities_iter(cities_xml):
    city_info_pattern = re.compile(r'"id": (.+?),.+?'
                                   r'"addr:region": "(.+?)".+?'
                                   r'"name": "(.+?)"',
                                   flags=re.DOTALL)

    cities_iter = city_info_pattern.finditer(cities_xml)
    return cities_iter


def write_result_in_txt():
    with open('cities_from_osm.txt', 'w', encoding='utf-8') as res:
        cities_xml = get_cities_xml()
        cities = get_cities_iter(cities_xml)
        for city in cities:
            print('{0},{1},{2}'.format(city[3], city[1], city[2]), file=res)


if __name__ == '__main__':
    write_result_in_txt()
