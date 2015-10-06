# -*- coding: utf-8 -*-
import tornado.web
from application.service.abroad import Abroad
from application.models.spot import CitySpotIds
from pola.machine.topic_model import GTopicModel
from pola.conversation import Conversation, Reaction
import json


class AgentBase(tornado.web.RequestHandler):
    CONVERSATION_KEY = "conversation_history"

    def _load_history(self):
        b = self.get_secure_cookie(self.CONVERSATION_KEY)
        if b:
            s = b.decode("utf-8")
            return json.loads(s)
        else:
            return []

    def get_history(self):
        from pola.conversation import Suggestion
        history = self._load_history()
        h = [Suggestion.deserialize(h) for h in history]
        return h

    def add_history(self, h):
        hs = h.serialize()
        history = self._load_history()
        history.append(hs)
        self.set_secure_cookie(self.CONVERSATION_KEY, json.dumps(history))


class AgentIndexHandler(AgentBase):

    def get(self, group_id):
        self.set_secure_cookie(self.CONVERSATION_KEY, json.dumps([]))
        self.render("agent.html")


class AgentHandler(AgentBase):
    BRAIN = None

    @classmethod
    def load_brain(cls, data_dir):
        import os

        data_file = ""
        model_file = ""

        for f in sorted(os.listdir(data_dir)):
            if not data_file and os.path.splitext(f)[1] == ".json":
                data_file = os.path.join(data_dir, f)
            elif not model_file and os.path.splitext(f)[1] == ".gensim":
                model_file = os.path.join(data_dir, f)

        if data_file and model_file:
            cls.BRAIN = Conversation.load(GTopicModel, model_file, CitySpotIds, data_file)

    def get_brain(self):
        h = self.get_history()
        b = self.BRAIN.clone(h)
        return b

    def get(self, group_id):
        """
        suggest the plan to user
        :param group_key:
        :return:
        """

        _budget = int(self.get_argument("budget", default=0))
        if _budget == 0:
            budget = 50000
        elif _budget == 1:
            budget = 100000
        elif _budget == 2:
            budget = 150000

        s = self.__suggest()
        self.write(s)

    def post(self, group_id):
        """
        receive feedback from user
        :param group_key:
        :return:
        """

        candidate_id = self.get_argument("candidate_id", default="")
        is_like = self.get_argument("is_like", default="false")
        feedback = Reaction.positive
        if is_like == "false":
            feedback = Reaction.negative

        s = self.__suggest(feedback)
        self.write(s)

    def __suggest(self, feedback=Reaction.neutral):
        brain = self.get_brain()
        candidates = brain.suggest(feedback, count=3)
        suggest = brain.history[-1]

        ab = Abroad()
        r = suggest.serialize()

        def load(c):
            cs = ab.load_city_spots(c)
            tours = ab.get_tour(cs.city.code)
            s = cs.serialize()
            s["tours"] = tours
            return s

        cities = [load(c) for c in candidates]
        r["candidates"] = [c for c in cities if len(c["tours"]) > 0]
        self.add_history(suggest)

        return r


class ResultHandler(AgentHandler):

    def get(self, group_id):
        self.render("result.html")

    def post(self, group_id):
        brain = self.get_brain()
        history = self.get_history()
        budget = int(self.get_argument("budget", default=0))

        def serialize(h):
            _h = h.serialize()
            _h["candidates"] = [brain.candidates[i].serialize() for i in _h["candidate_ids"]]
            return _h

        shistory = {
            "result": [serialize(h) for h in history]
        }

        # self.clear_cookie(self.CONVERSATION_KEY)
        self.write(shistory)
