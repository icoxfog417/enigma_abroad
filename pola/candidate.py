class Candidate():

    def __init__(self, candidate_id):
        self.candidate_id = candidate_id

    @classmethod
    def deserialize(cls, serialized):
        raise Exception("You have to implements how to parse deserialize object")

    def serialize(self):
        raise Exception("You have to implements how to serialize object")

    @classmethod
    def to_doc(cls, candidates, lang="ja"):
        raise Exception("You have to implements how to convert object array to Document object")

    @classmethod
    def load(cls, path):
        import os
        from pola.machine.topic_model.resource import FileResource
        from pola.machine.topic_model.resource import PickleResource

        ext = os.path.splitext(os.path.basename(path))[1].lower()
        candidates = []
        if ext == "txt":
            r = FileResource(path)
            candidates = r.load(deserializer=cls.__init__)
        elif ext == "pickle":
            r = PickleResource(path)
            candidates = r.load()

        return candidates
