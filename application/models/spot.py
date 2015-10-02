from collections import namedtuple
from pola.candidate import Candidate
from pola.machine.topic_model.document import Document


class Item():

    def __init__(self, code, name, name_en=""):
        self.code = code
        self.name = name
        self.name_en = name_en

    @classmethod
    def deserialize(cls, serialized):
        item = Item(
            serialized["code"],
            serialized["name"],
            "" if not "name_en" in serialized else serialized["name_en"]
        )
        return item


class City(Item):

    def __init__(self, code, name, country, area, lat=-1.0, lng=-1.0, name_en=""):
        super(City, self).__init__(code, name, name_en)
        self.country = country
        self.area = area
        self.lat = float(lat)
        self.lng = float(lng)

    @classmethod
    def deserialize(cls, serialized):
        j = serialized
        base = Item.deserialize(j)
        country = Item.deserialize(j["country"])
        area = Item.deserialize(j["area"])

        city = City(base.code, base.name, country, area,
                    j["lat"],
                    j["lng"],
                    name_en=base.name_en)

        return city

    def __hash__(self):
        return hash((self.code, self.name))

    def __eq__(self, other):
        return (self.code, self.name) == (other.code, other.name)


class Spot(Item):

    def __init__(self, code, name, title, description, url, area, country, city, lat, lng, map_scale, name_en=""):
        super(Spot, self).__init__(code, name, name_en)
        self.title = title
        self.description = description
        self.url = url
        self.area = area
        self.country = country
        self.city = city
        self.lat = -1 if not lat else float(lat)
        self.lng = -1 if not lng else float(lng)
        self.map_scale = -1 if not map_scale else float(map_scale)

    @classmethod
    def deserialize(cls, serialized):
        j = serialized
        base = Item.deserialize(j)
        area = Item.deserialize(j["area"])
        country = Item.deserialize(j["country"])
        citybase = Item.deserialize(j["city"])
        city = City(citybase.code, citybase.name, country, area)

        spot = Spot(base.code, base.name,
                    j["title"],
                    j["description"],
                    j["url"],
                    area,
                    country,
                    city,
                    j["lat"],
                    j["lng"],
                    j["map_scale"],
                    name_en=base.name_en)

        return spot


class CitySpots(Candidate):

    def __init__(self, spot):
        super(CitySpots, self).__init__(spot.city.code)
        self.city = spot.city
        self.spots = [spot]

    @classmethod
    def deserialize(cls, serialized):
        raise Exception("You can't create CitySpot by deserialize")

    def serialize(self):
        raise Exception("You can't serialize CitySpot")

    @classmethod
    def to_doc(cls, candidates, lang="ja"):
        descs = []
        for c in candidates:
            descs.append("\n".join([s.title + " " + s.description for s in c.spots]))
        return Document.load_docs(descs, lang=lang)

    @classmethod
    def load(cls, path):
        import json
        city_dict = {}

        with open(path, "r", encoding="utf-8") as f:
            spotjs = json.load(f)
            spots = [Spot.deserialize(s) for s in spotjs]

        for s in spots:
            if s.city.code not in city_dict:
                city_dict[s.city.code] = CitySpots(s)
            else:
                city_dict[s.city.code].spots.append(s)

        city_spots = [v for v in city_dict.values()]
        return city_spots

    def __str__(self):
        string = "{0}:{1}".format(self.candidate_id, self.city.name)
        return string
