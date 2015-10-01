# -*- coding: utf-8 -*-
import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from pola.machine.topic_model.resource import PickleResource
from pola.machine.topic_model.resource import FileResource


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edit corpus of spot document.")

    parser.add_argument("--path", type=str, help="path to spots document file (pickle).")
    parser.add_argument("--save", nargs="?", type=bool, const=True, default=False, help="save result.")
    parser.add_argument("--under", type=int, default=-1, help="cut under the n count word.")
    parser.add_argument("--above", type=float, default=-1, help="cut above the n or n% count word.")
    parser.add_argument("--freq", type=float, default=-1, help="cut above the n% frequency word in documents.")
    parser.add_argument("--ignore", type=str, default="", help="ignore words list file (only file name, locate in path folder).")

    args = parser.parse_args()
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "../data/cityspots_doc.pickle")

    p = PickleResource(path)
    doc = p.load()

    if args.freq > 0:
        doc.cut_frequent(args.freq)

    doc.cut_pos({"pos": ["動詞", "副詞"], "class1": ["接尾", "副詞可能"], "class2": ["人名", "地域", "副詞可能"]})

    if args.under > 0:
        doc.cut_under(args.under)

    if args.above > 0:
        doc.cut_above(args.above)

    if args.ignore:
        ig_path = os.path.join(os.path.dirname(path), args.ignore)
        ig = FileResource(ig_path)
        words = ig.load()
        for w in words:
            doc.remove_vocab(w[0])

    doc.show_vocab(show_pos=True)

    if args.save:
        fname = os.path.basename(path)
        doc_fname = os.path.splitext(fname)[0] + "_edited.pickle"
        doc_path = os.path.join(os.path.dirname(path), "./" + doc_fname)

        pe = PickleResource(doc_path)
        pe.save(doc)
