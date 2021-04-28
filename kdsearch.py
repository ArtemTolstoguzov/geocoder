import math
from geo import Geo
from operator import itemgetter

RAD = math.pi / 180


def convert_meters_to_degrees(lat, lon, meters):
    a = 6378137
    e2 = 0.006694380004260827
    lon_m = (math.pi * a * math.cos(lon * RAD)) / \
            (180 * math.sqrt(1 - e2 * math.sin(lon * RAD) ** 2))
    lat_m = 111134.861111
    return meters / lat_m, meters / lon_m


def get_rectangle_neighbors(
        lines, number, depth, lat, lon, offset_lat, offset_lon, geo_list):
    if number < len(lines) and lines[number] != '#\n':
        info = lines[number].split(';')
        item = Geo((info[1], info[0]), ('hash', info[2], info[3], info[4],
                                        float(info[-2]), float(info[-1])))
        if (math.fabs(item.lat - lat) <= offset_lat
                and math.fabs(item.lon - lon) <= offset_lon):
            geo_list.append(item)
        if depth % 2 == 1:
            if item.lon > lon + offset_lon:
                get_rectangle_neighbors(lines, number * 2, depth + 1, lat, lon,
                                        offset_lat, offset_lon, geo_list)
            elif item.lon < lon - offset_lon:
                get_rectangle_neighbors(lines, number * 2 + 1, depth + 1, lat,
                                        lon, offset_lat, offset_lon, geo_list)
            else:
                get_rectangle_neighbors(lines, number * 2, depth + 1, lat, lon,
                                        offset_lat, offset_lon, geo_list)
                get_rectangle_neighbors(lines, number * 2 + 1, depth + 1, lat,
                                        lon, offset_lat, offset_lon, geo_list)
        else:
            if item.lat > lat + offset_lat:
                get_rectangle_neighbors(lines, number * 2, depth + 1, lat, lon,
                                        offset_lat, offset_lon, geo_list)
            elif item.lat < lat - offset_lat:
                get_rectangle_neighbors(lines, number * 2 + 1, depth + 1, lat,
                                        lon, offset_lat, offset_lon, geo_list)
            else:
                get_rectangle_neighbors(lines, number * 2, depth + 1, lat, lon,
                                        offset_lat, offset_lon, geo_list)
                get_rectangle_neighbors(lines, number * 2 + 1, depth + 1, lat,
                                        lon, offset_lat, offset_lon, geo_list)


def get_distance(llat1, llon1, llat2, llon2):
    lat1 = llat1 * RAD
    lat2 = llat2 * RAD
    lon1 = llon1 * RAD
    lon2 = llon2 * RAD
    cl1 = math.cos(lat1)
    sl1 = math.sin(lat1)
    rad = 6372795
    cl2 = math.cos(lat2)
    sl2 = math.sin(lat2)
    delta = lon2 - lon1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)
    y = math.sqrt(cl2 * sdelta * cl2 * sdelta
                  + (cl1 * sl2 - sl1 * cl2 * cdelta)
                  * (cl1 * sl2 - sl1 * cl2 * cdelta))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    dist = ad * rad
    return dist


def get_neighbors(geo, radius):
    with open('kdtree.txt', 'r', encoding='utf8') as tf:
        lines = tf.readlines()
        neighbors = []
        get_rectangle_neighbors(lines, 1, 1, geo.lat, geo.lon, *(
            convert_meters_to_degrees(geo.lat, geo.lon, radius)), neighbors)
        neighbors = [(get_distance(geo.lat, geo.lon, n.lat, n.lon), n)
                     for n in neighbors]
        neighbors = [n for n in filter(lambda b: b[0] <= radius, neighbors)]
        return sorted(neighbors, key=itemgetter(0))
