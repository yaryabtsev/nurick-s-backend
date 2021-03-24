import os
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from database.base import db_session, init_db
from database.order import Order
from database.courier import Courier
from validator.validator import Validator
import pickle

app = Flask(__name__)
app.debug = True
validator = Validator()


@app.route('/couriers', methods=['POST'])
def post_couriers():
    if not request.is_json:
        raise BadRequest('Content-Type must be validator/json')
    import_data = request.get_json()
    errors = validator.couriers(import_data)
    if errors:
        return jsonify(errors), 400
    couriers = {'couriers': []}
    for courier in import_data['data']:
        curr_courier = Courier.query.filter_by(courier_id=courier['courier_id']).first()
        if not curr_courier:
            new_courier = Courier(updated_at=datetime.now(), courier_id=courier['courier_id'],
                                  courier_type=courier['courier_type'],
                                  regions=pickle.dumps(courier['regions']),
                                  working_hours=pickle.dumps(courier['working_hours']))
            db_session.add(new_courier)
            couriers['couriers'].append({'id': courier['courier_id']})
        else:
            raise BadRequest(f'couriers with courier_id={courier["courier_id"]} already exists')
    db_session.commit()
    return jsonify(couriers), 201


@app.route('/orders', methods=['POST'])
def post_orders():
    if not request.is_json:
        raise BadRequest('Content-Type must be validator/json')
    import_data = request.get_json()
    errors = validator.orders(import_data)
    if errors:
        return jsonify(errors), 400
    orders = {'orders': []}
    for order in import_data['data']:
        curr_order = Order.query.filter_by(courier_id=order['order_id']).first()
        if not curr_order:
            new_order = Order(updated_at=datetime.now(), order_id=order['order_id'],
                              weight=order['weight'], region=order['region'],
                              delivery_hours=pickle.dumps(order['delivery_hours']), assign_time=datetime(1, 1, 1),
                              complete_time=datetime(1, 1, 1), courier_id=0)
            db_session.add(new_order)
            orders['orders'].append({'id': order['order_id']})
        else:
            raise BadRequest(f'couriers with order_id={order["order_id"]} already exists')
    db_session.commit()
    return jsonify(orders), 201


@app.route('/orders/assign', methods=['POST'])
def post_orders_assign():
    if not request.is_json:
        raise BadRequest('Content-Type must be validator/json')
    import_data = request.get_json()
    errors = validator.orders_assign(import_data)
    if errors:
        return jsonify(errors), 400
    courier = Courier.query.filter_by(courier_id=import_data["courier_id"]).first()
    if not courier:
        raise BadRequest('incorrect id')
    max_weight = 10
    if courier.courier_type == "bike":
        max_weight = 15
    elif courier.courier_type == "car":
        max_weight = 50
    regions = pickle.loads(courier.regions)
    orders = Order.query.filter(Order.assign_time == datetime(1, 1, 1), Order.courier_id == 0,
                                Order.complete_time == datetime(1, 1, 1),
                                Order.weight <= max_weight, Order.region in regions)
    response = {"orders": [], "assign_time": ""}
    for order in orders:
        if check_date(order.delivery_hours, courier.working_hours):
            order.assign_time = datetime.now()
            order.courier_id = courier.courier_id
            order.updated_at = datetime.now()
            response["orders"].append({'id': order['orders_id']})
    response["assign_time"] = "{}-{}-{}T{}:{}.{}Z".format(*[_ for _ in datetime.now().timetuple()][:6])
    db_session.commit()
    return jsonify(response), 200


@app.route('/orders/complete', methods=['POST'])
def post_orders_complete():
    if not request.is_json:
        raise BadRequest('Content-Type must be validator/json')
    import_data = request.get_json()
    errors = validator.orders_is_complete(import_data)
    if errors:
        return jsonify(errors), 400
    order = Order.query.filter_by(order_id=import_data["order_id"], courier_id=import_data["courier_id"],
                                  complete_time=datetime(1, 1, 1)).first()
    if not order:
        raise BadRequest('incorrect ids')
    order.complete_time = datetime.now()
    order.updated_at = datetime.now()
    courier = Courier.query.filter_by(courier_id=import_data["courier_id"]).first()
    if not order:
        raise BadRequest('incorrect courier_id')
    c = 2
    if courier.courier_type == "bike":
        c = 5
    elif courier.courier_type == "car":
        c = 9
    courier.earnings += 500 * c
    # TODO: update rating
    courier.updated_at = datetime.now()
    db_session.commit()
    return jsonify({"order_id": import_data["order_id":]}), 200


def check_date(delivery_hours, working_hours):
    timeline = pickle.loads(delivery_hours) + pickle.loads(working_hours)
    for i in range(len(timeline)):
        timeline[i] = [list(map(int, _.split(':'))) for _ in timeline[i].split('-')]
    timeline.sort()
    for i in range(1, len(timeline)):
        if timeline[i][0] <= timeline[i - 1][1]:
            return True
    return False


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def update_couriers(courier_id):
    if not request.is_json:
        raise BadRequest('Content-Type must be validator/json')
    import_data = request.get_json()
    errors = validator.patch_courier_id(import_data)
    if errors:
        return jsonify(errors), 400
    courier = Courier.query.filter_by(courier_id=courier_id).first()
    if not courier:
        raise BadRequest('incorrect id')
    for key in import_data:
        if key in ["regions", "working_hours"]:
            courier.__dict__[key] = pickle.dumps(import_data[key])
        else:
            courier.__dict__[key] = import_data[key]
    json_courier = {}
    for key in ["courier_id", "courier_type", "regions", "working_hours"]:
        if key in ["regions", "working_hours"]:
            json_courier[key] = pickle.loads(courier.__dict__[key])
        else:
            json_courier[key] = courier.__dict__[key]
    orders = Order.query.filter_by(courier_id=courier.courier_id, complete_time=datetime(1, 1, 1))
    max_weight = 10
    if courier.courier_type == "bike":
        max_weight = 15
    elif courier.courier_type == "car":
        max_weight = 50
    regions = pickle.loads(courier.regions)
    for order in orders:
        if order.weight > max_weight or order.region not in regions or not check_date(order.delivery_hours,
                                                                                      courier.working_hours):
            order.courier_id = 0
            order.assign_time = datetime(1, 1, 1)
            order.updated_at = datetime.now()
    courier.updated_at = datetime.now()
    db_session.commit()
    return jsonify(json_courier), 200


@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_couriers(courier_id):
    courier = Courier.query.filter_by(courier_id=courier_id).first()
    if not courier:
        raise BadRequest('incorrect id')
    json_courier = {}
    for key in ["courier_id", "courier_type", "regions", "working_hours", "rating", "earnings"]:
        if key == "rating" and courier.rating == 0:
            continue
        if key in ["regions", "working_hours"]:
            json_courier[key] = pickle.loads(courier.__dict__[key])
        else:
            json_courier[key] = courier.__dict__[key]
    return jsonify(json_courier)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def hello_world():
    return "Hell world!", 200


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    init_db()
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '8080'))
    except ValueError:
        PORT = 5005
    app.run(HOST, PORT)
