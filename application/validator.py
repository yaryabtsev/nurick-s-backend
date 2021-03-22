import os
import json
import jsonschema
from jsonschema import ValidationError


class Validator:
    def __init__(self):
        self.couriers_data = _load_schema('post_schema.json')
        self.courier_info = _load_schema('courier_schema.json')
        self.patch_courier = _load_schema('patch_courier_id.json')

    def validate_couriers(self, data: dict) -> dict:
        validation_error = dict()
        try:
            jsonschema.validate(data, self.couriers_data)
        except ValidationError as ve:
            validation_error['validation_error'] = ve.message
            return validation_error

        # dictionary of id's that failed to validate
        incorrect_cour = dict()
        for courier in data['data']:
            try:
                jsonschema.validate(courier, self.courier_info)
            except ValidationError:
                if len(incorrect_cour) == 0:
                    incorrect_cour['couriers'] = list()
                incorrect_cour['couriers'].append({'id':  courier.get('courier_id')})
        if len(incorrect_cour) != 0:
            validation_error['validation_error'] = incorrect_cour

        # checking courier's ids are unique
        couriers_ids = {courier.get('courier_id') for courier in data['data']}
        if len(couriers_ids) != len(data['data']):
            validation_error['validation_error'] = 'Couriers ids are not unique'
        return validation_error

    def validate_patch_courier(self, data: dict) -> dict:
        validation_error = dict()
        try:
            jsonschema.validate(data, self.patch_courier)
        except ValidationError as ve:
            validation_error['validation_error'] = ve.message
        return validation_error


def _load_schema(file_name: str) -> dict:
    with open(os.path.join(os.path.dirname(__file__), 'schemas', file_name)) as json_file:
        return json.load(json_file)


v = Validator()
dict_data = {"data": [
    {"courier_id": 1, "courier_type": "foot", "regions": [1, 12, 22], "working_hours": ["11:35-14:05", "09:00-11:00"]},
    {"courier_id": 2, "courier_type": "bike", "regions": [22, 1], "working_hours": ["09:00-18:00"]},
    {"courier_id": 3, "courier_type": "car", "regions": [12, 22, 23, 33], "working_hours": ["09:00-18:00"]}]
             }

print(v.validate_couriers(dict_data))



