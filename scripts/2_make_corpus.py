# -*- coding: utf-8 -*-
import sys
import os
import argparse
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from application.models.salon import Salon
from pola.machine.topic_model.resource import PickleResource

if __name__ == "__main__":
    # for command line tool
    parser = argparse.ArgumentParser(description="Make corpus from salons data file.")
    parser.add_argument("path", type=str, help="path to salon data file (json format).")
    args = parser.parse_args()

    # load salon data
    path = args.path
    salons = Salon.load(path)

    # save as document
    salon_doc = Salon.to_doc(salons)
    mood_doc = Salon.to_mood_doc(salons)

    print("show salon's corpus")
    salon_doc.show_vocab(limit=20)

    print("show mood's corpus")
    mood_doc.show_vocab(limit=20)

    for d in [("salon", salon_doc), ("mood", mood_doc)]:
        doc_path = os.path.join(os.path.dirname(args.path), "./" + d[0] + "_doc.pickle")
        p = PickleResource(doc_path)
        p.save(d[1])
