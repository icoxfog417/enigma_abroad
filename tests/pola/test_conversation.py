# -*- coding: utf-8 -*-
import os
import unittest
import json
from pola.machine.topic_model.document import Document
import pola.machine.topic_model.resource as rs
from pola.candidate import Candidate
from pola.conversation import Conversation, Reaction


class TCandidate(Candidate):

    def __init__(self, obj_id, title, description):
        super(TCandidate, self).__init__(obj_id)
        self.title = title
        self.description = description

    @classmethod
    def deserialize(cls, serialized):
        j = json.loads(serialized)
        o = cls(j["obj_id"], j["title"], j["description"])
        return o

    def serialize(self):
        j = json.dumps(self.__dict__)
        return j

    @classmethod
    def to_doc(cls, candidates, lang="ja"):
        descs = [c.description for c in candidates]
        return Document.load_docs(descs, lang=lang)


class TestConversation(unittest.TestCase):
    SPOTS_STORE = "spots.txt"

    def test_conversation(self):
        from pola.machine.topic_model import TopicModel
        candidates, doc = self.create_candidates()
        r = rs.MCMCResource(self.make_path("test_conv_model.pickle"))
        r.remove()

        model = TopicModel(2, doc, r)
        print("topic model conversation")
        self.execute_conversation(model, candidates)

    def test_g_conversation(self):
        from pola.machine.topic_model import GTopicModel
        candidates, doc = self.create_candidates()
        r = rs.GensimResource(self.make_path("test_conv_gmodel.gensim"))
        r.remove()
        model = GTopicModel(2, doc, r)

        print("gensim topic model conversation")
        self.execute_conversation(model, candidates)

    def execute_conversation(self, model, candidates):
        c = Conversation(model, candidates, initial_topic=0)
        c.model.train()

        reactions = [Reaction.neutral, Reaction.positive, Reaction.negative, Reaction.negative, Reaction.positive]
        for i, r in enumerate(reactions):
            s = c.suggest(r, count=1)
            print(c.history[-1])
            if i > 0:
                if r == Reaction.positive:
                    self.assertEqual(c.history[-1].topic, c.history[-2].topic)
                if r == Reaction.negative:
                    self.assertNotEqual(c.history[-1].topic, c.history[-2].topic)

    def create_candidates(self):
        """
        from trip advisor
        http://www.tripadvisor.co.uk/TravelersChoice-Destinations-cTop-g1
        :return:
        """

        # a,b is similar topic, c,d is similar topic (and different from a,b)
        data = [
            (0, "a", "aaa bbb bbb bbb aaa aaa aaa"),
            (1, "b", "bbb bbb bbb bbb bbb aaa aaa"),
            (2, "c", "ccc ddd ddd ddd ccc ccc ccc"),
            (3, "d", "ddd ddd ddd ddd ddd ccc ccc"),
        ]
        candidates = [TCandidate(*d) for d in data]
        return candidates, TCandidate.to_doc(candidates, "en")

    def make_path(self, fname):
        path = os.path.dirname(__file__)
        return os.path.join(path, "../data/" + fname)
