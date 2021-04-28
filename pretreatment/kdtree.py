import sqlite3
from geo import Geo
from collections import deque

TREE_DEPTH = 0


class KDTree:
    def __init__(self, geo_list, depth):
        if len(geo_list) == 1:
            self.item = geo_list[0]
            self.left = None
            self.right = None
            global TREE_DEPTH
            if depth > TREE_DEPTH:
                TREE_DEPTH = depth
            return

        if depth % 2 == 1:
            sorted_list = sorted(geo_list, key=lambda geo: geo.lon)
        else:
            sorted_list = sorted(geo_list, key=lambda geo: geo.lat)

        half = len(sorted_list) // 2
        self.item = sorted_list[half]
        left_side = sorted_list[0:half]
        right_side = sorted_list[half + 1:len(sorted_list)]

        self.left = None if len(left_side) == 0 \
            else KDTree(left_side, depth + 1)
        self.right = None if len(right_side) == 0 \
            else KDTree(right_side, depth + 1)

    @staticmethod
    def serialize_tree(tree, filename):
        with open(filename, 'w', encoding='utf8') as tf:
            print('0', file=tf)
            count = 0
            amount = 2**TREE_DEPTH - 1
            q = deque()
            q.append(tree)
            while count != amount:
                node = q.popleft()
                count += 1
                if node is None:
                    print('#', file=tf)
                    continue
                print(node.item, file=tf)
                q.append(node.left)
                q.append(node.right)


def get_geo_list():
    with sqlite3.connect('geocoder.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''select * from cities''')
        row = cursor.fetchall()
        geo_list = []
        for city in row:
            cursor.execute('''select * from "{0[2]}"'''.format(city))
            row = cursor.fetchall()
            geo_list += [Geo(city, building) for building in row]
    return geo_list


if __name__ == '__main__':
    tree = KDTree(get_geo_list(), 1)
    KDTree.serialize_tree(tree, 'tree.txt')
