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
    parser = argparse.ArgumentParser(description="Make corpus from tours data file.")
    parser.add_argument("--path", type=str, help="path to tour data file (json format).")
    args = parser.parse_args()

    # load tours data
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "../data/tours.json")
    tours = Tour.load(path)

    # save as document
    tour_doc = Tour.to_doc(tours)
    mood_doc = Tour.to_mood_doc(tours)

    print("show tours corpus")
    tour_doc.show_vocab(limit=20)

    print("show mood's corpus")
    mood_doc.show_vocab(limit=20)

    for d in [("tour", tour_doc), ("mood", mood_doc)]:
        doc_path = os.path.join(os.path.dirname(args.path), "./" + d[0] + "_doc.pickle")
        p = PickleResource(doc_path)
        p.save(d[1])
