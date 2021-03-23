import unittest
import os

import app


class BasicTestCase(unittest.TestCase):
    def test_index(self):
        tester = app.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database(self):
        tester = os.path.exists("database/data.db")
        self.assertEqual(tester, True)


class SomeTestCase(unittest.TestCase):
    def test_post_couriers_1(self):
        tester = app.app.test_client(self)
        json_data = {"data": [
            {"courier_id": 1, "courier_type": "foot", "regions": [1, 12, 22],
             "working_hours": ["11:35-14:05", "09:00-11:00"]},
            {"courier_id": 2, "courier_type": "bike", "regions": [22, 1], "working_hours": ["09:00-18:00"]},
            {"courier_id": 3, "courier_type": "car", "regions": [12, 22, 23, 33], "working_hours": ["09:00-18:00"]}]
        }
        #response = tester.post('/couriers', json=json_data)
        #self.assertEqual(response.status_code, 201)
        #self.assertEqual(response.json, {'couriers': [{'id': courier['courier_id']} for courier in json_data["data"]]})

    def test_patch_couriers_id_1(self):
        tester = app.app.test_client(self)
        json_data = {"courier_type": "bike"}
        response = tester.patch('/couriers/1', json=json_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"courier_id": 1, "courier_type": "bike", "regions": [1, 12, 22],
                                         "working_hours": ["11:35-14:05", "09:00-11:00"]})

    def test_post_orders_1(self):
        tester = app.app.test_client(self)
        json_data = {
            "data": [
                {"order_id": 1, "weight": 0.23, "region": 12, "delivery_hours": ["09:00-18:00"]},
                {"order_id": 2, "weight": 15, "region": 1, "delivery_hours": ["09:00-18:00"]},
                {"order_id": 3, "weight": 0.01, "region": 22, "delivery_hours": ["09:00-12:00", "16:00-21:30"]}]}
        #response = tester.post('/orders', json=json_data)
        #self.assertEqual(response.status_code, 201)
        #self.assertEqual(response.json, {'orders': [{'id': order['order_id']} for order in json_data["data"]]})


if __name__ == '__main__':
    unittest.main()
