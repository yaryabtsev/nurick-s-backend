import os
import json
import jsonschema
from jsonschema import ValidationError


def validate_couriers(data: dict) -> dict:
    couriers_data = _load_schema('post_schema.json')
    courier_info = _load_schema('courier_schema.json')
    validation_error = dict()
    try:
        jsonschema.validate(data, couriers_data)
    except ValidationError as ve:
        validation_error['validation_error'] = ve.message
        return validation_error

    # dictionary of id's that failed to validate
    incorrect_cour = dict()
    for courier in data['data']:
        try:
            jsonschema.validate(courier, courier_info)
        except ValidationError:
            if len(incorrect_cour) == 0:
                incorrect_cour['couriers'] = list()
            incorrect_cour['couriers'].append({'id': courier.get('courier_id')})
    if len(incorrect_cour) != 0:
        validation_error['validation_error'] = incorrect_cour

    # checking courier's ids are unique
    couriers_ids = {courier.get('courier_id') for courier in data['data']}
    if len(couriers_ids) != len(data['data']):
        validation_error['validation_error'] = 'Couriers ids are not unique'
    return validation_error


def validate_patch_courier(data: dict) -> dict:
    patch_courier = _load_schema('patch_courier_id.json')
    validation_error = dict()
    try:
        jsonschema.validate(data, patch_courier)
    except ValidationError as ve:
        validation_error['validation_error'] = ve.message
    return validation_error


def _load_schema(file_name: str) -> dict:
    with open(os.path.join(os.path.dirname(__file__), 'schemas', file_name)) as json_file:
        return json.load(json_file)
