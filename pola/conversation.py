from enum import Enum


class Reaction(Enum):
    positive = 1
    neutral = 0
    negative = -1


class Suggestion():

    def __init__(self, topic, candidate_ids, reaction):
        self.topic = topic
        self.candidate_ids = candidate_ids
        self.reaction = reaction

    def serialize(self):
        return {
            "topic": self.topic,
            "candidate_ids": self.candidate_ids,
            "reaction": self.reaction.value
        }

    @classmethod
    def deserialize(cls, d):
        s = Suggestion(d["topic"], d["candidate_ids"], Reaction(d["reaction"]))
        return s

    def __str__(self):
        return "{0} -> topic={1} suggest={2}".format(self.reaction, self.topic, ",".join([str(s) for s in self.candidate_ids]))

class Conversation():

    def __init__(self, model, candidates, initial_topic=-1):
        self.model = model
        self.candidates = candidates
        self.initial_topic = initial_topic
        self.history = []

    def clone(self, history=()):
        cloned = Conversation(self.model, self.candidates)
        cloned.history = self.history
        if len(history) > 0:
            cloned.history = history

        return cloned

    @classmethod
    def load(cls, model_class, model_path, candidate_class, candidates_path):
        model = model_class.load(model_path)
        candidates = candidate_class.load(candidates_path)
        c = Conversation(model, candidates)
        return c

    def suggest(self, reaction=Reaction.neutral, count=1):
        from random import randint
        random = randint(0, self.model.topic_count-1)
        t = -1
        candidates = []

        # initial
        if len(self.history) == 0:
            if self.initial_topic > -1:
                t = self.initial_topic
            else:
                t = random
        else:
            if reaction == Reaction.neutral:
                t = random
            elif reaction == Reaction.positive:
                t = self.history[-1].topic
            elif reaction == Reaction.negative:
                latest = self.history[-1].topic
                distances = self.model.calc_distances(latest)
                t = distances[-1][0]

        if t > -1:
            candidate_indices = self.model.get_topic_documents(t)
            suggested = []
            for h in self.history:
                suggested += h.candidate_ids
            candidate_ids = [i for i, p in candidate_indices if i not in suggested][:count]
            self.history.append(Suggestion(t, candidate_ids, reaction))
            candidates = [self.candidates[i] for i in candidate_ids]

        return candidates
