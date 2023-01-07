from . import BaseTestCase
import json


class TestApi(BaseTestCase):
    def test_buslocation(self):
        response = self.client.get("/api/buslocation")
        self.assertEqual(response.status_code, 200)

    def test_searchlinesfornone(self):
        response = self.client.get("/api/routes", query_string={"keyword": "公車"})
        # covert bytes array into JSON format
        self.assertEqual(json.loads(response.data)["data"], "查無路線資料")

    def test_searchlines(self):
        response = self.client.get("/api/routes", query_string={"keyword": "紅5"})
        # covert bytes array into JSON format
        self.assertIn("紅5", json.loads(response.data)["data"]["捷運紅線接駁公車"])

    def test_estimatetime(self):
        response = self.client.get(
            "/api/estimatetime",
            query_string={"latitude": 25.0462559043502, "longitude": 121.51700353811},
        )
        self.assertEqual(response.status_code, 200)

    def test_route(self):
        response = self.client.get("/api/route/紅5")
        self.assertEqual(response.status_code, 200)

    def test_routestatus(self):
        response = self.client.get("/api/routestatus/紅5")
        self.assertEqual(response.status_code, 200)

    def test_stoplocation(self):
        response = self.client.get("/api/stoplocation")
        self.assertEqual(response.status_code, 200)

    def test_stops_latlng(self):
        response = self.client.get(
            "/api/stops", query_string={"method": "latlng", "keyword": "25.046,121.517"}
        )
        self.assertEqual(response.status_code, 200)

    def test_stops_address(self):
        response = self.client.get(
            "/api/stops", query_string={"method": "address", "keyword": "台北市羅斯福路1號"}
        )
        self.assertEqual(response.status_code, 200)

    def test_stop(self):
        response = self.client.get(
            "/api/stop",
            query_string={"latitude": 25.0462559043502, "longitude": 121.51700353811},
        )
        self.assertEqual(response.status_code, 200)
