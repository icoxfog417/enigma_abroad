# -*- coding: utf-8 -*-
import unittest
from application.service.abroad import Abroad
from keyenv import get_api_key


class TestAbroad(unittest.TestCase):

    def test_get_city(self):
        ab = Abroad(get_api_key())
        city = ab.get_city("NYC")
        self.assertTrue(city)

    def test_load_city_spotids(self):
        from application.models.spot import CitySpotIds
        csi = CitySpotIds(
            "TXG",
            [
                "001096",
                "001076",
                "001099",
                "001094",
                "001093"
            ]
        )

        ab = Abroad(get_api_key())
        cs = ab.load_city_spots(csi)
        self.assertTrue(cs)
        self.assertEqual(len(csi.spot_ids), len(cs.spots))

    def test_get_tour(self):
        ab = Abroad(get_api_key())
        tours = ab.get_tour("BCN", "都市")
        self.assertTrue(len(tours) > 0)
        print(tours)
