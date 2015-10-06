# -*- coding: utf-8 -*-
import unittest
from application.service.abroad import Abroad


class TestAbroad(unittest.TestCase):

    def test_get_city(self):
        ab = Abroad()
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

        ab = Abroad()
        cs = ab.load_city_spots(csi)
        self.assertTrue(cs)
        self.assertEqual(len(csi.spot_ids), len(cs.spots))

    def test_get_tour(self):
        ab = Abroad()
        tours = ab.get_tour("TXG", "埔里市街")
        self.assertTrue(len(tours) > 0)
        print(tours)
