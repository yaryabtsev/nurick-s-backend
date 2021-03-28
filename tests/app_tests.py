import unittest
import app
import validator_tests
from database.courier import Courier
from database.order import Order


class AppTest(unittest.TestCase):
    def setUp(self):
        # Remove data from tables
        Courier.query.delete()
        Order.query.delete()

        # Add some GOLD data to tables
        app.testing = True
        tester = app.app.test_client(self)
        tester.post('/couriers', json=validator_tests.COURIERS_GOLD)
        tester.post('/orders', json=validator_tests.ORDERS_GOLD)

    def tearDown(self):
        app.db_session.commit()

    def test_post_couriers(self):
        tester = app.app.test_client(self)

        # id of courier already exists
        courier_data = {'data': [
            {'courier_id': 1, 'courier_type': 'foot', 'regions': [1], 'working_hours': ['11:35-14:05']}]}
        response = tester.post('/couriers', json=courier_data)
        self.assertEqual(400, response.status_code)

        courier_data['data'][0]['courier_id'] = -1
        response = tester.post('/couriers', json=courier_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'validation_error': {'couriers': [{'id': -1}]}}, response.json)

        courier_data['data'][0]['courier_id'] = 4
        courier_data['data'][0]['regions'] = [1, -2, 5, 7]
        response = tester.post('/couriers', json=courier_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'validation_error': {'couriers': [{'id': 4}]}}, response.json)

        courier_data = {'data': [
            {'courier_id': 14, 'courier_type': 'foot', 'regions': [1], 'working_hours': ['11:35-14:05']},
            {'courier_id': 24, 'courier_type': 'car', 'regions': [1, 2], 'working_hours': ['11:35-14:05']},
            {'courier_id': 34, 'courier_type': 'car', 'regions': [1, 2], 'working_hours': ['18:35-23:05']}]}
        response = tester.post('/couriers', json=courier_data)
        self.assertEqual(201, response.status_code)
        self.assertEqual({'couriers': [{'id': 14}, {'id': 24}, {'id': 34}]}, response.json)

    def test_post_orders(self):
        tester = app.app.test_client(self)

        # id of order already exists
        order_data = {'data': [{'order_id': 1, 'weight': 0.23, 'region': 12, 'delivery_hours': ['09:00-18:00']}]}
        response = tester.post('/orders', json=order_data)
        self.assertEqual(400, response.status_code)

        order_data['data'][0]['order_id'] = 4
        order_data['data'][0]['delivery_hours'] = ['09:00-18:00', '09:00-23:99']
        response = tester.post('/orders', json=order_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'validation_error': {'orders': [{'id': 4}]}}, response.json)

        order_data = {'data': [
            {'order_id': 15, 'weight': 0.23, 'region': 12, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 25, 'weight': 55, 'region': 33, 'delivery_hours': ['09:00-18:00']},
            {'order_id': 35, 'weight': 100, 'region': 22, 'delivery_hours': ['09:00-12:00', '16:00-21:30']}]}
        response = tester.post('/orders', json=order_data)
        self.assertEqual(201, response.status_code)
        self.assertEqual({'orders': [{'id': 15}, {'id': 25}, {'id': 35}]}, response.json)

    def test_patch_courier_id(self):
        tester = app.app.test_client(self)

        # id of courier does not exist
        patch_data = {'regions': [11, 33, 2]}
        response = tester.patch('/couriers/100', json=patch_data)
        self.assertEqual(400, response.status_code)

        response = tester.patch('/couriers/2', json=patch_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'courier_id': 2, 'courier_type': 'bike', 'regions': [11, 33, 2],
                          'working_hours': ['09:00-18:00']}, response.json)

    def test_order_assign(self):
        tester = app.app.test_client(self)

        # id of courier does not exist
        response = tester.post('orders/assign', json={'courier_id': 100})
        self.assertEqual(400, response.status_code)

        response = tester.post('orders/assign', json={'courier_id': 1})
        self.assertEqual(200, response.status_code)
        self.assertEqual({'тут assign time'}, response.json)



if __name__ == '__main__':
    unittest.main()
