# -*- coding: utf-8 -*-
import sys
import os
import argparse
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from application.models.spot import CitySpots
from pola.machine.topic_model.resource import PickleResource

if __name__ == "__main__":
    # for command line tool
    parser = argparse.ArgumentParser(description="Make corpus from tours data file.")
    parser.add_argument("--path", type=str, help="path to tour data file (json format).")
    args = parser.parse_args()

    # load tours data
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "../data/spots.json")
    cityspots = CitySpots.load(path)

    # create city information data
    cityspotsj = []
    for cs in cityspots:
        j = {
            "id": cs.city.code,
            "spots": [s.code for s in cs.spots]
        }
        cityspotsj.append(j)

    # save as document
    cityspots_doc = CitySpots.to_doc(cityspots)

    print("show city spots corpus")
    cityspots_doc.show_vocab(limit=20)

    doc_path = os.path.join(os.path.dirname(path), "./cityspots_doc.pickle")
    p = PickleResource(doc_path)
    p.save(cityspots_doc)

    # save as json file
    j = json.dumps(cityspotsj, indent=2, ensure_ascii=False)
    data_path = os.path.join(os.path.dirname(path), "./cityspots.json")
    with open(data_path, "wb") as f:
        f.write(j.encode("utf-8"))
