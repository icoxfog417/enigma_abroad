# -*- coding: utf-8 -*-
import os
import unittest
import numpy as np
from pola.machine.topic_model import Document
from pola.machine.topic_model import GTopicModel
from pola.machine.topic_model import resource as rs


class TestGTopicModel(unittest.TestCase):

    def test_model(self):
        model = self.create_test_model()
        model.train(iter=10000)
        print(model.perplexity())
        for t in model.core.print_topics():
            print(t)

    def test_save_and_load_model(self):
        pre_model = self.create_test_model()
        pre_model.train(iter=10000)
        p1 = pre_model.perplexity()
        pre_model.save()

        r = self.get_resource()
        post_model = GTopicModel.load(r.path)
        p2 = post_model.perplexity()
        self.assertTrue((p1 - p2) < 1e-5)

    def test_calc_distances(self):
        model = self.create_test_model()
        model.train()
        ds = model.calc_distances(0)
        self.assertTrue(2, len(ds))
        print(ds)

    def test_get_doc_indices(self):
        model = self.create_test_model()
        model.train()
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
        model = GTopicModel(3, doc, resource=r)
        return model

    def get_resource(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "../data/test_gmodel.gensim")
        return rs.GensimResource(path)
