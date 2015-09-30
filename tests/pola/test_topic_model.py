# -*- coding: utf-8 -*-
import os
import unittest
import numpy as np
from pola.machine.topic_model import Document
from pola.machine.topic_model import TopicModel
from pola.machine.topic_model import resource as rs


class TestTopicModel(unittest.TestCase):

    def test_model(self):
        model = self.create_test_model()
        model.train()
        print(model.perplexity())

    def test_model_gensim(self):
        doc = self.get_doc_en()
        from gensim import models
        corpus = doc.archives
        model = models.ldamodel.LdaModel(corpus, num_topics=3)
        print(np.exp(-model.log_perplexity(corpus)))

    def test_save_and_load_model(self):
        batch_size = 100

        pre_model = self.create_test_model()
        pre_model.train(iter=batch_size, burn=0)
        self.assertTrue(len(pre_model.core.trace("z_0")[:]) == batch_size)
        pre_z = [z.value for z in pre_model.variables["z"]]
        p1 = pre_model.perplexity()
        pre_model.save()

        r = self.get_resource()
        post_model = TopicModel.load(r.path)
        post_z = [z.value for z in post_model.variables["z"]]
        for i, z in enumerate(post_z):
            self.assertEqual(0, sum(z != pre_z[i]))
        p2 = post_model.perplexity()

        post_model.train(iter=batch_size, burn=0)
        self.assertTrue(len(post_model.core.trace("z_0", chain=None)[:]) == (2 * batch_size))
        self.assertEqual(p1, p2)

    def test_kldiv(self):
        p = np.array([[0.1, 0.4, 0.3, 0.9]])
        q1 = np.array([[0.1, 0.2, 0.2, 0.5]])
        q2 = np.array([[0.1, 0.4, 0.3, 0.8]])

        self.assertTrue(TopicModel.kldiv(p, p) == 0)

        d1 = TopicModel.kldiv(p, q1)
        self.assertGreater(d1, 0)
        d2 = TopicModel.kldiv(p, q2)
        self.assertGreater(d1, d2)

    def test_calc_distances(self):
        model = self.create_test_model()
        model.train(iter=100, burn=10)
        ds = model.calc_distances(0)
        self.assertTrue(2, len(ds))
        print(ds)

    def test_get_doc_indices(self):
        model = self.create_test_model()
        model.train(iter=100, burn=10)
        print(model.get_topic_documents(0))

    def get_doc_en(self):
        docs = [
            "I read the news today oh boy About a lucky man who made the grade",
            "I saw a film today oh boy The English Army had just won the war",
            "It’s been a hard days night, and I been working like a dog",
            "It’s been a hard days night, I should be sleeping like a dog",
            "You say you want a revolution",
            "You tell me that it's evolution"
        ]
        doc = Document.load_docs(docs, lang="en")
        return doc

    def create_test_model(self):
        r = self.get_resource()
        r.remove()

        doc = self.get_doc_en()
        model = TopicModel(3, doc, resource=r)
        return model

    def get_resource(self):
        path = os.path.dirname(__file__)
        mc = rs.MCMCResource(os.path.join(path, "../data/test_mcmc.pickle"))

        return mc
