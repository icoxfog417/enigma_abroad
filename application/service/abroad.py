from enum import Enum
import requests


class Abroad():
    URL_FORMAT = "http://webservice.recruit.co.jp/ab-road/{0}/v1/"

    def __init__(self):
        import os
        self.api_key = os.environ.get("RECRUIT_API_KEY")

        if not self.api_key:
            keyfile = os.path.join(os.path.dirname(__file__), "../../key.json")
            if os.path.isfile(keyfile):
                import json
                with open(keyfile, "r", encoding="utf-8") as f:
                    key_json = json.load(f)
                    self.api_key = key_json["api_key"]

    def get_city(self, city_code):
        from application.models.spot import City

        url = self.URL_FORMAT.format("city")

        params = {
            "key": self.api_key,
            "city": city_code,
            "format": "json",
            "count": 1
        }

        resp = requests.get(url, params=params)
        body = self.__extract_body(resp, "city")
        city = None

        if body:
            city = City.deserialize(body[0])

        return city

    def get_spots(self, code_or_codes):
        from application.models.spot import Spot

        url = self.URL_FORMAT.format("spot")

        params = {
            "key": self.api_key,
            "spot": code_or_codes,
            "format": "json"
        }

        resp = requests.get(url, params=params)
        body = self.__extract_body(resp, "spot")
        spots = []

        if body:
            spots = [Spot.deserialize(b) for b in body]

        return spots

    def load_city_spots(self, city_spot_ids):
        from application.models.spot import CitySpots
        spots = self.get_spots(city_spot_ids.spot_ids)
        cs = CitySpots(spot=spots[0])
        cs.spots = spots
        return cs

    def get_tour(self, city_code, spot_name="", dept="", ym="", price_max="", count=5):
        url = self.URL_FORMAT.format("tour")

        params = {
            "key": self.api_key,
            "city": city_code,
            "count": count,
            "format": "json"
        }

        if spot_name:
            params["keyword"] = spot_name

        if dept:
            params["dept"] = dept

        if ym:
            params["ym"] = ym

        if price_max:
            params["price_max"] = price_max

        resp = requests.get(url, params=params)
        body = self.__extract_body(resp, "tour")
        tours = [] if not body else body

        return tours

    def __extract_body(self, resp, key):
        body = {}
        if resp.ok:
            js = resp.json()
            if "results" in js and key in js["results"]:
                body = js["results"][key]

        return body
