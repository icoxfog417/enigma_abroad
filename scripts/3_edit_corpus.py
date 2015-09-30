import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from pola.machine.topic_model.resource import PickleResource
from pola.machine.topic_model.resource import FileResource


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edit corpus of spot document.")

    parser.add_argument("path", type=str, help="path to spots document file (pickle).")
    parser.add_argument("--save", nargs="?", type=bool, const=True, default=False, help="save result.")
    parser.add_argument("--under", type=int, default=-1, help="cut under the n count word.")
    parser.add_argument("--above", type=int, default=-1, help="cut above the n count word.")
    parser.add_argument("--ignore", type=str, default="", help="ignore words list file (only file name, locate in path folder).")

    args = parser.parse_args()

    p = PickleResource(args.path)
    doc = p.load()

    if args.under > 0:
        doc.cut_under(args.under)

    if args.above > 0:
        doc.cut_above(args.above)

    if args.ignore:
        ig_path = os.path.join(os.path.dirname(args.path), args.ignore)
        ig = FileResource(ig_path)
        words = ig.load()
        for w in words:
            doc.remove_vocab(w[0])

    doc.show_vocab()

    if args.save:
        fname = os.path.basename(args.path)
        doc_fname = os.path.splitext(fname)[0] + "_edited.pickle"
        doc_path = os.path.join(os.path.dirname(args.path), "./" + doc_fname)

        pe = PickleResource(doc_path)
        pe.save(doc)
