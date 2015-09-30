import os
import re


class Word():

    def __init__(self,
                 surface,
                 pos="*",
                 class1="*",
                 class2="*",
                 class3="*",
                 conjugated_form="*",
                 conjugated_type="*",
                 origin_form="*",
                 interpretation="*",
                 pronunciation="*"
                 ):

        self.surface = surface
        self.pos = pos
        self.class1 = class1
        self.class2 = class2
        self.class3 = class3
        self.conjugated_form = conjugated_form
        self.conjugated_type = conjugated_type
        self.origin_form = origin_form
        self.interpretation = interpretation
        self.pronunciation = pronunciation


class Parser():

    def __init__(self):
        self.stop_words = []

    def parse(self, text):
        words = self.parse_all(text)
        words = [w for w in words if not self.is_excepted(w)]
        return words

    def parse_all(self, text):
        raise Exception("You have to implements parse method")

    def is_excepted(self, word):
        return False

    @classmethod
    def read_stop_words(cls, filename):
        stop_words = []
        path = os.path.join(os.path.dirname(__file__), "./data/" + filename)
        with open(path, "rb") as f:
            lines = f.readlines()
            for ln in lines:
                sw = ln.decode("utf-8").replace(os.linesep, "")
                if sw:
                    stop_words.append(sw)

        return stop_words

class JapaneseParser(Parser):

    def __init__(self):
        super(JapaneseParser, self).__init__()
        self.stop_words = self.read_stop_words("japanese_stop_words.txt")

    def parse_all(self, text):
        import MeCab

        words = []
        t = MeCab.Tagger()
        node = t.parseToNode(text)
        while node:
            r = node.feature.split(",")
            if r[0] != "BOS/EOS":
                words.append(Word(*([r[-3]] + r)))  # use origin_form as surface
            node = node.next

        return words

    def is_excepted(self, word):
        e = False
        if len(word.surface) <= 1:
            e = True
        if word.surface in self.stop_words:
            e = True
        elif word.pos in ["助詞", "助動詞", "前置詞", "冠詞", "記号"] or word.pos.startswith("接"):
            e = True
        elif word.pos == "動詞" and word.class1 in ["接尾"]:
            e = True

        return e

class EnglishParser(Parser):

    def __init__(self):
        super(EnglishParser, self).__init__()

    def parse_all(self, text):
        trim = lambda t: re.sub(r"[\.\'\"\s]", "", t)

        words = text.split(" ")
        words = [Word(trim(w).lower()) for w in words]

        return words

    def is_excepted(self, word):
        e = False
        if len(word.surface) <= 1:
            e = True
        if word.surface in self.stop_words:
            e = True

        return e
