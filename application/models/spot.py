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

    def serialize(self):
        return self.__dict__

    def _sub_serialize(self):
        j = {}
        d = self.__dict__
        for k in d:
            if isinstance(d[k], Item):
                j[k] = d[k].serialize()
            else:
                j[k] = d[k]
        return j


class City(Item):

    def __init__(self, code, name, country, area, lat=-1.0, lng=-1.0, name_en=""):
        super(City, self).__init__(code, name, name_en)
        self.country = country
        self.area = area
        self.lat = float(lat)
        self.lng = float(lng)
        self.raw = {}

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
        city.raw = serialized
        return city

    def serialize(self):
        if self.raw:
            return self.raw
        else:
            return self._sub_serialize()


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
        self.raw = {}

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

        spot.raw = serialized

        return spot

    def serialize(self):
        if self.raw:
            return self.raw
        else:
            return self._sub_serialize()


class CitySpots(Candidate):

    def __init__(self, city=None, spot=None):
        if city:
            super(CitySpots, self).__init__(city.code)
            self.city = city
            self.spots = []
        else:
            super(CitySpots, self).__init__(spot.city.code)
            self.city = spot.city
            self.spots = [spot]

    @classmethod
    def deserialize(cls, serialized):
        raise Exception("You can't create CitySpot by deserialize")

    def serialize(self):
        s = {
            "city": self.city.serialize(),
            "spots": [s.serialize() for s in self.spots]
        }
        return s

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
                city_dict[s.city.code] = CitySpots(spot=s)
            else:
                city_dict[s.city.code].spots.append(s)

        city_spots = [v for v in city_dict.values()]
        return city_spots

    def __str__(self):
        string = "{0}:{1}".format(self.candidate_id, self.city.name)
        return string


class CitySpotIds(Candidate):

    def __init__(self, city_id, spot_ids=()):
        super(CitySpotIds, self).__init__(city_id)
        self.spot_ids = [] if len(spot_ids) == 0 else spot_ids

    @classmethod
    def deserialize(cls, serialized):
        csi = CitySpotIds(
            serialized["id"],
            [i for i in serialized["spots"]],
        )
        return csi

    def serialize(self):
        j = {
            "id": self.candidate_id,
            "spots": self.spot_ids
        }
        return j

    @classmethod
    def to_doc(cls, candidates, lang="ja"):
        raise Exception("CitySpotIds is not used to create document.")

    @classmethod
    def load(cls, path):
        import json
        cityspotids = []

        with open(path, "r", encoding="utf-8") as f:
            js = json.load(f)
            cityspotids = [CitySpotIds.deserialize(j) for j in js]

        return cityspotids
