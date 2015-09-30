import numpy as np
from collections import namedtuple
from gensim import models
from pola.machine.topic_model.model import Model


class GTopicModel(Model):

    def __init__(self, topic_count, doc, resource, **kwargs):
        super(GTopicModel, self).__init__(topic_count, doc, resource, **kwargs)

    def build(self):
        id2word = dict([(i[0], i[1].surface) for i in self.doc.vocab.items()])
        model = models.ldamodel.LdaModel(num_topics=self.topic_count, id2word=id2word)
        return model

    def train(self, iter=5000, burn=1000, verbose=False, **kwargs):
        corpus = self.doc.archives
        self.core.update(corpus, iterations=iter)

    def perplexity(self, test_doc=None):
        doc = test_doc.archives if test_doc else self.doc.archives
        p = np.exp(-self.core.log_perplexity(doc))
        return p

    def calc_distances(self, topic):
        # get probability to each words
        # https://github.com/piskvorky/gensim/blob/develop/gensim/models/ldamodel.py#L733

        t = self.core.state.get_lambda()
        for i, p in enumerate(t):
            t[i] = t[i] / t[i].sum()

        base = t[topic]
        distances = [(i_p[0], self.kldiv(base, i_p[1])) for i_p in enumerate(t) if i_p[0] != topic]
        distances = sorted(distances, key=lambda d: d[1])
        return distances

    def get_document_topics(self, index):
        rate = self.core.__getitem__(self.doc.archives[index], -1)
        return rate

    def get_topic_documents(self, topic):
        docs = []
        for i, a in enumerate(self.doc.archives):
            p = 0
            p_topic = [p for p in self.core[a] if p[0] == topic]
            if len(p_topic) > 0:
                p = p_topic[0][1]
            docs.append((i, p))

        docs = sorted(docs, key=lambda d: d[1], reverse=True)
        return docs

    def get_topic_words(self, topic, topn=10):
        return self.core.show_topic(topic, topn=topn)
