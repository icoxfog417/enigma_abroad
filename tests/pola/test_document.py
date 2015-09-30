# -*- coding: utf-8 -*-
import unittest
from collections import Counter
import MeCab
from pola.machine.topic_model import Document


class TestDocument(unittest.TestCase):

    def test_mecab(self):
        s = "名古屋城は非常に美しい城ですね"
        t = MeCab.Tagger()

        result = []
        node = t.parseToNode(s)
        while node:
            r = node.feature.split(",")
            if r[0] != "BOS/EOS":
                result.append(r)
            node = node.next

        self.assertTrue(len(result) > 0)
        print(result)

    def test_document(self):
        d = self.get_documents()
        doc = Document.load_docs(d)
        self.assertEqual(len(d), len(doc.archives))

        c = Counter()
        for a in doc.archives:
            for v in a:
                c[v[0]] += v[1]
        freq = c.most_common()
        get_freq = lambda j: [f for f in freq if f[0] == j][0][1]

        for i, v in enumerate(doc.vocab):
            self.assertEqual(doc.frequency[i], get_freq(i))

        doc.cut_under(1)
        for k, v in sorted(doc.frequency.items(), reverse=True, key=lambda f: f[1]):
            print(doc.vocab[k].surface, v)

    def test_cut_tail(self):
        d = self.get_documents()
        doc = Document.load_docs(d)
        freq = 1
        remained = [f for f in doc.frequency.items() if f[1] > freq]

        doc.cut_under(freq)
        self.assertEqual(len(remained), len(doc.vocab.keys()))
        self.assertEqual(len(remained), len(doc.frequency.keys()))

    def test_remove(self):
        import random
        d = self.get_documents()
        doc = Document.load_docs(d)
        confirmation_id = len(doc.vocab) - 1

        def get_info(target_id):
            v = doc.vocab[target_id]
            f = doc.frequency[target_id]
            c = len([w for w in [a for a in doc.archives] if w[0] == target_id])
            return (v, f, c)

        removed = ["食材"]
        old_v = get_info(confirmation_id)
        i = doc.remove_vocab(removed[0])
        target = random.sample(list(doc.vocab.keys())[:-2], 1)[0]
        removed += [doc.vocab[target].surface]
        doc.remove_vocab(target)

        new_id = doc.get_id(old_v[0].surface)
        new_v = get_info(new_id)

        self.assertEqual(new_v[0].surface, old_v[0].surface)
        self.assertEqual(new_v[1], old_v[1])
        self.assertEqual(new_v[2], old_v[2])

        for r in removed:
            self.assertEqual(-1, doc.get_id(r))

    def test_split(self):
        d = self.get_documents()
        doc = Document.load_docs(d)

        right_size = 1
        ld, rd = doc.split(right_rate_or_size=right_size)

        self.assertEqual(len(d) - right_size, len(ld.archives))
        self.assertEqual(right_size, len(rd.archives))

        self.assertLess(len(ld.vocab), len(doc.vocab))
        self.assertLess(len(rd.vocab), len(ld.vocab))

    def get_documents(self):
        d = [
            "お台場の新名所、ダイバーシティ東京の屋上にあるバーベキューテラス。食材、飲物持込可能なスタイルのバーベキュー場だが、食材(要予約)・飲み物も用意されているので手ぶらでもOK。機材や炭の片付け不要なので、気軽にバーベキューを楽しめる。",
            "新豊洲駅前にある約1.6ヘクタールの都市型アウトドアパーク。オートキャンプ場の「THE THIRD PARK」には約50のテントサイトがあり、日帰りバーベキューも可能。機材、食材、片付けなどがおまかせの「フルセットコース」と、サイトをレンタルする「セルフサイトコース」がある。さわやかな潮風とスカイツリーや東京タワーなどの眺望も楽しみ。カーゴトレーラー型CAFE「PITMASTERS」、発信型イベントスペース「CONTAINER」なども要チェック。",
            "ゆりかもめ有明駅前の首都圏直下型地震に備え作られた防災拠点「東京臨海広域防災公園内」に誕生した『そなエリア東京バーベキューガーデン』は、リーズナブルな価格で利用できる手ぶらバーベキューガーデン。食材セットを予約すれば、手軽にバーベキューが楽しめるプランが多数用意されている。また、隣接している防災体験学習施設では、防災体験ツアーを体験することができる。一般の来園・来館者用の駐車場はないので、公共交通機関を利用の事。"
        ]
        return d
