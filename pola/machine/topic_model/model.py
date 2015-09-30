import os
import numpy as np
from pola.machine.topic_model import resource as rs


class Model():
    METADATA_EXT = "metadata.pickle"

    def __init__(self, topic_count, doc, resource, **kwargs):

        self.topic_count = topic_count
        self.doc = doc
        self.minimum_probability = 0.01

        self.variables = kwargs
        if "minimum_probability" in self.variables:
            self.minimum_probability = self.variables.pop("minimum_probability")

        self.resource = resource
        model = self.build()
        self.core = model

    @classmethod
    def get_metadata_resource(cls, path):
        fname = os.path.basename(path)
        metadata_path = os.path.join(os.path.dirname(path), "./" + (os.path.splitext(fname)[0]) + "_" + cls.METADATA_EXT)
        mr = rs.PickleResource(metadata_path)
        return mr

    @classmethod
    def load(cls, path):
        mr = cls.get_metadata_resource(path)
        m = mr.load()
        model = m.build()

        if not os.path.isfile(m.resource.path):
            alternative = os.path.join(os.path.dirname(path), os.path.basename(m.resource.path))
            m.resource.path = alternative

        m.core = m.resource.load(model=model)

        return m

    def save(self, metadata_path=""):
        self.resource.save(self.core)
        self.core = None
        self.variables = {}

        if hasattr(self.resource, "path"):
            mr = self.get_metadata_resource(self.resource.path)
            mr.save(self)
        else:
            if not metadata_path:
                raise Exception("You have to set metadatapath when save.")
            else:
                mr = self.get_metadata_resource(metadata_path)
                mr.save(self)

    def build(self):
        raise Exception("You have to implements model build method")

    def train(self, iter=5000, burn=1000, verbose=False, **kwargs):
        raise Exception("You have to implements how to train the model")

    def perplexity(self, test_doc=None):
        raise Exception("You have to implements how to calculates the perplexity")

    @classmethod
    def kldiv(self, p, q):
        distance = np.sum(p * np.log(p / q))
        return distance

    def calc_distances(self, topic):
        raise Exception("You have to implements how to calculates the distances between topics")

    def get_document_topics(self, index):
        raise Exception("You have to implements how to get document's topics")

    def get_topic_documents(self, topic):
        raise Exception("You have to implements how to get topic's documents")

    def get_topic_words(self, topic, topn=10):
        raise Exception("You have to implements how to get words in topic")
