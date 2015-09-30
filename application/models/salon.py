from pola.candidate import Candidate
from pola.machine.topic_model.document import Document


class Mood():

    def __init__(self, photo, caption):
        self.photo = photo
        self.caption = caption


class Feature():

    def __init__(self, code, name, g_code, g_name, photos, caption, description):
        self.code = code
        self.name = name
        self.g_code = g_code
        self.g_name = g_name
        self.photo = photos
        self.caption = caption
        self.description = description


class Salon(Candidate):

    def __init__(self,
                 salon_id,
                 url,
                 name,
                 description,
                 kodawari,
                 image,
                 moods,
                 features,
                 lat=-1.0,
                 lng=-1.0,
                 page_rank=-1
                 ):
        super(Salon, self).__init__(salon_id)
        self.salon_id = salon_id
        self.url = url
        self.name = name
        self.description = description
        self.kodawari = kodawari
        self.image = image
        self.moods = moods
        self.features = features
        self.lat = -1.0 if not lat else float(lat)
        self.lng = -1.0 if not lng else float(lng)
        self.page_rank = page_rank

    @classmethod
    def deserialize(cls, serialized):
        s = Salon(
            serialized["id"],
            serialized["urls"]["pc"],
            serialized["name"],
            serialized["description"],
            serialized["kodawari"],
            serialized["main"]["photo"]["m"],
            [Mood(m["photo"], m["caption"]) for m in serialized["mood"]],
            [Feature(f["code"], f["name"], f["g_code"], f["g_name"], f["photo"], f["caption"], f["description"]) for f in serialized["feature"]],
            serialized["lat"],
            serialized["lng"]
        )
        return s

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
    def to_mood_doc(cls, candidates, lang="ja"):
        moods = ["\n".join([m.caption for m in s.moods]) for s in candidates]
        return Document.load_docs(moods, lang=lang)

    @classmethod
    def load(cls, path):
        import json
        page_size_for_rank = 20
        salons = []

        def deserialize(i, j):
            rank = i // page_size_for_rank
            s = Salon.deserialize(j)
            s.page_rank = rank
            return s

        with open(path, "r", encoding="utf-8") as f:
            salons_j = json.load(f)
            salons = [deserialize(*ij) for ij in enumerate(salons_j)]

        return salons

def __str__(self):
        string = "{0}:{1}".format(self.salon_id, self.name)
        return string
