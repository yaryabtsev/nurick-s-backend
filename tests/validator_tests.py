import unittest
from validator.validator import Validator

COURIERS_GOLD = {'data': [
    {'courier_id': 1, 'courier_type': 'foot', 'regions': [1, 12, 22], 'working_hours': ['11:35-14:05', '09:00-11:00']},
    {'courier_id': 2, 'courier_type': 'bike', 'regions': [22, 1], 'working_hours': ['09:00-18:00']},
    {'courier_id': 3, 'courier_type': 'car', 'regions': [12, 22, 23, 33], 'working_hours': ['09:00-18:00']},
    {'courier_id': 4, 'courier_type': 'foot', 'regions': [1, 12, 22], 'working_hours': ['11:35-14:05', '09:00-11:00']},
    {'courier_id': 5, 'courier_type': 'bike', 'regions': [22, 1], 'working_hours': ['09:00-18:00']},
    {'courier_id': 6, 'courier_type': 'car', 'regions': [12, 22, 23, 33], 'working_hours': ['09:00-18:00']}]}

ORDERS_GOLD = {'data': [
    {'order_id': 1, 'weight': 0.23, 'region': 12, 'delivery_hours': ['09:00-18:00']},
    {'order_id': 2, 'weight': 15, 'region': 1, 'delivery_hours': ['09:00-18:00']},
    {'order_id': 3, 'weight': 0.01, 'region': 22, 'delivery_hours': ['09:00-12:00', '16:00-21:30']},
    {'order_id': 4, 'weight': 100, 'region': 12, 'delivery_hours': ['09:00-18:00']},
    {'order_id': 5, 'weight': 20, 'region': 1, 'delivery_hours': ['09:00-18:00']},
    {'order_id': 6, 'weight': 14.5, 'region': 22, 'delivery_hours': ['09:00-12:00', '16:00-21:30']}]
}


class ValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = Validator()

    def test_couriers(self):
        self.assertFalse(self.validator.couriers(COURIERS_GOLD))

        temp_couriers = COURIERS_GOLD.copy()
        temp_couriers['data'][0]['courier_id'] = 0
        self.assertDictEqual({'validation_error': {'couriers': [{'id': 0}]}}, self.validator.couriers(temp_couriers))

        temp_couriers['data'][1]['regions'] = []
        self.assertDictEqual({'validation_error': {'couriers': [{'id': 0}, {'id': 2}]}},
                             self.validator.couriers(temp_couriers))

        temp_couriers['data'][1]['regions'] = [12, 2]
        temp_couriers['data'][2]['working_hours'] = ['9:00-18:00']
        self.assertDictEqual({'validation_error': {'couriers': [{'id': 0},{'id': 3}]}},
                             self.validator.couriers(temp_couriers))

    def test_orders(self):
        self.assertFalse(self.validator.orders(ORDERS_GOLD))

        temp_order = ORDERS_GOLD.copy()
        temp_order['data'][0]['weight'] = 0
        self.assertDictEqual({'validation_error': {'orders': [{'id': 1}]}}, self.validator.orders(temp_order))

        temp_order['data'][0]['weight'] = 1
        temp_order['data'][1]['region'] = -1
        self.assertDictEqual({'validation_error': {'orders': [{'id': 2}]}}, self.validator.orders(temp_order))

        temp_order['data'][1]['region'] = 13
        temp_order['data'][0]['add_attribute'] = 0
        self.assertDictEqual({'validation_error': {'orders': [{'id': 1}]}}, self.validator.orders(temp_order))

    def test_orders_assign(self):
        orders_assign = {'courier_id': 2}
        self.assertFalse(self.validator.orders_assign(orders_assign))

        orders_assign = {}
        self.assertDictEqual({'validation_error': "'courier_id' is a required property"},
                             self.validator.orders_assign(orders_assign))

        orders_assign = {'courier_id': -2}
        self.assertDictEqual({'validation_error': '-2 is less than or equal to the minimum of 0'},
                             self.validator.orders_assign(orders_assign))

    def test_patch_courier(self):
        patch_courier = {
            'courier_type': 'foot',
            'regions': [11, 33, 2],
            'working_hours': ['09:00-18:00']}
        self.assertFalse(self.validator.patch_courier_id(patch_courier))

        patch_courier['working_hours'].append('25:00-36:99')
        self.assertTrue(self.validator.patch_courier_id(patch_courier))

        patch_courier['working_hours'] = ['09:00-18:00']
        patch_courier['courier_type'] = 'bike'
        self.assertFalse(self.validator.patch_courier_id(patch_courier))

        patch_courier = {}
        self.assertDictEqual({'validation_error': '{} does not have enough properties'},
                             self.validator.patch_courier_id(patch_courier))

        patch_courier['add_attribute'] = 0
        self.assertTrue(self.validator.patch_courier_id(patch_courier))

    def test_orders_is_complete(self):
        temp_gold = {'courier_id': 2, 'order_id': 33, 'complete_time': '2021-12-10T10:33:01.42Z'}
        self.assertFalse(self.validator.orders_is_complete(temp_gold))

        temp_gold['complete_time'] = '2021-13-10T10:33:01.42Z'
        self.assertDictEqual({'validation_error': "'2021-13-10T10:33:01.42Z' is not a 'date-time'"},
                             self.validator.orders_is_complete(temp_gold))

        temp_gold['complete_time'] = '2021-12-12T10:33:01.42Z'
        temp_gold['courier_id'] = 0
        self.assertDictEqual({'validation_error': '0 is less than or equal to the minimum of 0'},
                             self.validator.orders_is_complete(temp_gold))

        temp_gold['courier_id'] = 2
        temp_gold['add_attribute'] = 0
        self.assertTrue(self.validator.orders_is_complete(temp_gold))


if __name__ == '__main__':
    unittest.main()
