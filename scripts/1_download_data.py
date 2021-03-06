# -*- coding: utf-8 -*-
import sys
import os
import argparse
import json
import urllib.parse
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

def load_spots(api_key, page_size=100, limit=10000):
    API_ROOT = "http://webservice.recruit.co.jp/ab-road/spot/v1/"

    def make_params(start):
        return {
            "key": api_key,
            "start": start,
            "count": page_size,
            "format": "json"
        }

    spots = []
    index = 0
    timing = 10
    _limit = limit
    border = _limit / timing
    while index < _limit:
        # fetch spots
        p = make_params(index + 1)
        url = API_ROOT + "?" + urllib.parse.urlencode(p)
        resp = requests.get(url)

        # retrieve results
        if resp.ok:
            body = resp.json()
            if "results" in body and "spot" in body["results"]:
                results = body["results"]
                spotjs = results["spot"]
                count = len(spotjs)
                page = index // page_size
                max_count = int(results["results_available"])
                if max_count < _limit:
                    _limit = max_count
                    if index == 0:
                        border = _limit / timing

                for sj in spotjs:
                    spots.append(sj)

                index += count
                if index > border:
                    print("done {0} / {1}".format(index, _limit))
                    border += (_limit / timing)

            else:
                raise Exception("can not retrieve the results")
        else:
            resp.raise_for_status()

    return spots

if __name__ == "__main__":
    # for command line tool
    parser = argparse.ArgumentParser(description="Download data from recruit ab-road api.")
    parser.add_argument("key", type=str, help="key for recruit api.")
    parser.add_argument("--path", type=str, default="", help="path of data folder.")
    parser.add_argument("--limit", type=int, default=-1, help="cut under the n count word.")
    args = parser.parse_args()

    # preparation
    key = args.key
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "../data/")

    # extract data
    spots = []
    if args.limit < 0:
        spots = load_spots(key)
    else:
        spots = load_spots(key, limit=args.limit)

    # save as json file
    j = json.dumps(spots, indent=2, ensure_ascii=False)
    path = os.path.join(path, "spots.json")
    with open(path, "wb") as f:
        f.write(j.encode("utf-8"))
