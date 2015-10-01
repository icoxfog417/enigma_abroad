# -*- coding: utf-8 -*-
from collections import Counter
from pola.machine.topic_model import parser as ps


class Document():

    def __init__(self, lang, parser=None):
        self.__vocab_to_id = {}
        self.lang = lang
        self.vocab = {}
        self.frequency = {}
        self.archives = []

        self.parser = parser
        if not self.parser:
            if lang == "ja":
                self.parser = ps.JapaneseParser()
            else:
                self.parser = ps.EnglishParser()

    def get_id(self, surface):
        if surface in self.__vocab_to_id:
            return self.__vocab_to_id[surface]
        else:
            return -1

    @classmethod
    def load_docs(cls, docs, lang="ja"):
        doc = Document(lang)
        for d in docs:
            doc.add_doc(d)
        return doc

    def add_doc(self, doc):
        _words = self.parser.parse(doc)

        c = Counter()
        for w in _words:
            i = self.__add_vocab(w)
            c[i] += 1

        d = c.most_common()
        self.archives.append(d)

    def __add_vocab(self, v):
        if v.surface in self.__vocab_to_id:
            index = self.__vocab_to_id[v.surface]
            self.frequency[index] += 1
        else:
            index = len(self.vocab)
            self.__vocab_to_id[v.surface] = index
            self.vocab[index] = v
            self.frequency[index] = 1

        return self.__vocab_to_id[v.surface]

    def remove_vocab(self, vid_or_str, compaction=True):
        index = vid_or_str
        if isinstance(vid_or_str, str):
            if vid_or_str in self.__vocab_to_id:
                index = self.__vocab_to_id[vid_or_str]
            else:
                index = -1

        if index > -1 and index in self.vocab:
            for i, a in enumerate(self.archives):
                self.archives[i] = [ic for ic in a if ic[0] != index]

            self.__vocab_to_id.pop(self.vocab[index].surface)
            self.frequency.pop(index)
            self.vocab.pop(index)

            if compaction:
                self.__compact()

    def __compact(self):
        """
        re-order the id.
        :return:
        """

        # build mapping from old id -> new id
        idmap = dict(zip(self.vocab.keys(), range(len(self.vocab))))

        self.vocab = dict((idmap[v_id], v) for v_id, v in self.vocab.items())
        self.frequency = dict((idmap[v_id], f) for v_id, f in self.frequency.items())
        self.__vocab_to_id = dict((w, idmap[v_id]) for w, v_id in self.__vocab_to_id.items())

        for i, a in enumerate(self.archives):
            for j, w in enumerate(a):
                self.archives[i][j] = (idmap[w[0]], w[1])

    def cut_under(self, frequency):
        target = [i for i in self.frequency.items() if i[1] <= frequency]

        for t in target:
            self.remove_vocab(t[0], compaction=False)
        self.__compact()

    def cut_above(self, frequency):
        border = frequency
        if 0 < frequency < 1:
            border = len(self.archives) * frequency

        target = [i for i in self.frequency.items() if i[1] >= border]
        for t in target:
            self.remove_vocab(t[0], compaction=False)

        self.__compact()

    def cut_frequent(self, frequency):
        o = Counter()
        for a in self.archives:
            for f in a:
                o[f[0]] += 1

        target = [t for t in o.most_common() if t[1] / len(self.archives) >= frequency]
        for t in target:
            self.remove_vocab(t[0], compaction=False)

        self.__compact()

    def cut_pos(self, definition):
        target = []
        arr = lambda x: x if isinstance(x, (list, tuple)) else [x]
        for v in self.vocab:
            if "class1" in definition and self.vocab[v].class1 in arr(definition["class1"]):
                target.append(v)
            if "class2" in definition and self.vocab[v].class2 in arr(definition["class2"]):
                target.append(v)
            if "class3" in definition and self.vocab[v].class3 in arr(definition["class3"]):
                target.append(v)
            elif "pos" in definition and self.vocab[v].pos in arr(definition["pos"]):
                target.append(v)

        for v in target:
            self.remove_vocab(v, compaction=False)

        self.__compact()

    def split(self, right_rate_or_size=0.3, compact=True):
        import random
        size = 0
        if isinstance(right_rate_or_size, float):
            import math
            size = math.floor(len(self.archives) * right_rate_or_size)
        else:
            size = right_rate_or_size

        indices = range(len(self.archives))
        right_index = random.sample(indices, size)

        left = []
        right = []

        for i in indices:
            if i in right_index:
                right.append(self.archives[i])
            else:
                left.append(self.archives[i])

        def archive_to_doc(a):
            doc = Document(self.lang, self.parser)
            doc.archives = a
            for d in doc.archives:
                for c in d:
                    v_id = c[0]
                    v_f = c[1]
                    if v_id not in doc.vocab:
                        doc.vocab[v_id] = self.vocab[v_id]
                        doc.__vocab_to_id[self.vocab[v_id].surface] = v_id

                    if v_id not in doc.frequency:
                        doc.frequency[v_id] = 0
                    doc.frequency[v_id] += v_f

            return doc

        left_doc = archive_to_doc(left)
        right_doc = archive_to_doc(right)

        if compact:
            left_doc.__compact()
            right_doc.__compact()

        return left_doc, right_doc

    def reset(self):
        self.__vocab_to_id = {}
        self.vocab = {}
        self.frequency = {}
        self.archives = []

    def __len__(self):
        return len(self.archives)

    def __getitem__(self, index):
        return self.archives[index]

    def __iter__(self):
        return iter(self.archives)

    def elements(self, i):
        elements = []
        for vc in self.archives[i]:
            elements += ([vc[0]] * vc[1])

        return elements

    def vocab_keys(self):
        return self.vocab.keys()

    def show_vocab(self, limit=-1, show_pos=False):
        target = sorted(self.frequency.items(), reverse=True, key=lambda f: f[1])
        if limit > 0:
            target = target[:limit] + target[-limit:]

        counter = 0
        for k, v in target:
            p = self.vocab[k].surface
            if show_pos:
                p += "(" + ",".join([self.vocab[k].pos, self.vocab[k].class1, self.vocab[k].class2, self.vocab[k].class3]) + ")"

            print(p, v)
            counter += 1
            if counter == limit:
                print("----------(top {0} / under {0})----------".format(limit))
