import unittest
import os

import app


class BasicTestCase(unittest.TestCase):
    def test_index(self):
        tester = app.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database(self):
        tester = os.path.exists("data.db")
        self.assertEqual(tester, True)


class SomeTestCase(unittest.TestCase):
    def test_post_couriers(self):
        tester = app.app.test_client(self)
        json_data = {"data": [
            {"courier_id": 1, "courier_type": "foot", "regions": [1, 12, 22],
             "working_hours": ["11:35-14:05", "09:00-11:00"]},
            {"courier_id": 2, "courier_type": "bike", "regions": [22, 1], "working_hours": ["09:00-18:00"]},
            {"courier_id": 3, "courier_type": "car", "regions": [12, 22, 23, 33], "working_hours": ["09:00-18:00"]}]
        }
        response = tester.post('/couriers', json=json_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'couriers': [{'id': courier['courier_id']} for courier in json_data["data"]]})


if __name__ == '__main__':
    unittest.main()
