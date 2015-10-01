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

    def __init__(self, code, name, country, area, lat, lng, name_en=""):
        super(City, self).__init__(code, name, name_en)
        self.country = country
        self.area = area
        self.lat = float(lat)
        self.lng = float(lng)

    @classmethod
    def deserialize(cls, serialized):
        base = Item.deserialize(serialized)
        country = Item.deserialize(serialized["country"])
        area = Item.deserialize(serialized["area"])

        city = City(base.code, base.name, country, area,
                    serialized["lat"],
                    serialized["lng"],
                    name_en=base.name_en)

        return city


class Schedule():

    def __init__(self, city, day):
        self.city = city
        self.day = int(day)

    @classmethod
    def deserialize(cls, serialized):
        city = City.deserialize(serialized)
        sche = Schedule(
            city,
            serialized["day"]
        )
        return sche

Url = namedtuple("Url", ["qr", "mobile", "pc"])
Price = namedtuple("Price", ["min", "max"])
Image = namedtuple("Image", ["large", "middel", "small", "caption"])

class Theme(Item):

    def __init__(self, code, name, group, category):
        super(Theme, self).__init__(code, name)
        self.group = group
        self.category = category

    @classmethod
    def deserialize(cls, serialized):
        base = Item.deserialize(serialized)
        group = Item.deserialize(serialized["group"])
        category = Item.deserialize(serialized["category"])

        theme = Theme(
            base.code,
            base.name,
            group,
            category
        )

        return theme


class Tour(Candidate):

    def __init__(self,
                 tour_id,
                 title,
                 url,
                 price,
                 last_updated,
                 hotel_summary,
                 airline_summary,
                 city_summary,
                 themes,
                 kodawari,
                 brand,
                 departure,
                 destination,
                 schedules
                 ):
        super(Tour, self).__init__(tour_id)
        self.title = title
        self.url = url
        self.price = price
        self.last_updated = last_updated
        self.hotel_summary = hotel_summary
        self.airline_summary = airline_summary
        self.city_summary = city_summary
        self.themes = themes
        self.kodawari = kodawari
        self.brand = brand
        self.departure = departure
        self.destination = destination
        self.schedules = schedules
        self.order = -1

    @classmethod
    def deserialize(cls, serialized):
        j = serialized  # alias for varibale
        t = Tour(
            j["id"],
            j["title"],
            Url(**j["urls"]),
            Price(j["price"]["min"], j["price"]["max"]),
            j["last_update"],
            j["hotel_summary"],
            j["airline_summary"],
            j["city_summary"],
            [Theme.deserialize(t) for t in j["theme"]],
            [Item.deserialize(k) for k in j["kodawari"]],
            Item.deserialize(j["brand"]),
            Item.deserialize(j["dept"]),
            City.deserialize(j["dest"]),
            [Schedule.deserialize(s) for s in j["sche"]]
        )
        return t

    def serialize(self):
        dic = self.__dict__
        dic["moods"] = [m.__dict__ for m in self.moods]
        dic["features"] = [f.__dict__ for f in self.features]

        return dic

    @classmethod
    def to_doc(cls, candidates, lang="ja"):
        descs = ["\n".join([s.description, s.kodawari]) for s in candidates]
        return Document.load_docs(descs, lang=lang)

    @classmethod
    def load(cls, path):
        import json
        tours = []

        def deserialize(i, j):
            t = Tour.deserialize(j)
            t.order = i
            return s

        with open(path, "r", encoding="utf-8") as f:
            tourjs = json.load(f)
            tours = [deserialize(*ij) for ij in enumerate(tourjs)]

        return tours

    def __str__(self):
        string = "{0}:{1}".format(self.candsalon_id, self.name)
        return string
