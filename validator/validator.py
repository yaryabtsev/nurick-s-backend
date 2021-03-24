import os
import json
import jsonschema
from jsonschema import ValidationError


class Validator:
    def __init__(self):
        self.post_schema = _load_schema('post_schema.json')
        self.courier_info_schema = _load_schema('courier_schema.json')
        self.patch_courier_id_schema = _load_schema('patch_courier_id.json')
        self.orders_info_schema = _load_schema('orders_schema.json')
        self.orders_is_complete_schema = _load_schema('post_orders_complete.json')
        self.orders_assign_schema = _load_schema('orders_assign.json')

    def couriers(self, data: dict) -> dict:
        validation_error = _validate_schema(data, self.post_schema)
        if validation_error:
            return validation_error

        # dictionary of id's that failed to validate
        incorrect_couriers = dict()
        for courier in data['data']:
            try:
                jsonschema.validate(courier, self.courier_info_schema)
            except ValidationError:
                if len(incorrect_couriers) == 0:
                    incorrect_couriers['couriers'] = list()
                incorrect_couriers['couriers'].append({'id': courier['courier_id']})
        if len(incorrect_couriers) != 0:
            validation_error['validation_error'] = incorrect_couriers
        return validation_error

    def orders(self, data: dict) -> dict:
        validation_error = _validate_schema(data, self.post_schema)
        if validation_error:
            return validation_error

        incorrect_orders = dict()
        for order in data['data']:
            try:
                jsonschema.validate(order, self.orders_info_schema)
            except ValidationError:
                if len(incorrect_orders) == 0:
                    incorrect_orders['orders'] = list()
                incorrect_orders['orders'].append({'id': order['order_id']})
            if len(incorrect_orders) != 0:
                validation_error['validation_error'] = incorrect_orders
        return validation_error

    def orders_assign(self, data: dict) -> dict:
        return _validate_schema(data, self.orders_assign_schema)

    def patch_courier_id(self, data: dict) -> dict:
        return _validate_schema(data, self.patch_courier_id_schema)

    def orders_is_complete(self, data: dict) -> dict:
        return _validate_schema(data, self.orders_is_complete_schema)


def _validate_schema(data: dict, schema: dict) -> dict:
    validation_error = dict()
    try:
        jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())
    except ValidationError as ve:
        validation_error['validation_error'] = ve.message

    return validation_error


def _load_schema(file_name: str) -> dict:
    with open(os.path.join(os.path.dirname(__file__), 'schemas', file_name)) as json_file:
        return json.load(json_file)
