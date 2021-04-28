class Geo:
    def __init__(self, city_info, address_info):
        self.region = city_info[1]
        self.city = city_info[0]
        self.streettype = address_info[1]
        self.street = address_info[2]
        self.housenumber = address_info[3]
        self.lat = address_info[4]
        self.lon = address_info[5]

    def __str__(self):
        return f'{self.region};{self.city};{self.streettype};{self.street};' \
               f'{self.housenumber};{self.lat};{self.lon}'
