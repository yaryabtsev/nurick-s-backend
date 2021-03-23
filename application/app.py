import os
from datetime import datetime

from flask import Flask, request, Response, jsonify
from werkzeug.exceptions import BadRequest

from database import Courier, db_session, init_db, Order
from validator import validate_couriers, validate_patch_courier
import pickle

app = Flask(__name__)
app.debug = True


@app.route('/couriers', methods=['POST'])
def post_couriers():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')
    import_data = request.get_json()
    errors = validate_couriers(import_data)
    if errors:
        return jsonify(errors), 400
    couriers = {"couriers": []}
    for courier in import_data['data']:
        newCourier = Courier(updated_at=datetime.now(), courier_id=courier["courier_id"],
                             courier_type=courier["courier_type"], regions=pickle.dumps(courier["regions"]),
                             working_hours=pickle.dumps(courier["working_hours"]))
        # TODO: sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: couriers.courier_id
        db_session.add(newCourier)
        couriers["couriers"].append({'id': courier['courier_id']})
    db_session.commit()
    print(Courier.query.all())
    return jsonify(couriers), 200


@app.route('/orders', methods=['POST'])
def post_orders():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')
    import_data = request.get_json()
    # TODO:errors = validate_orders(import_data)
    # if errors:
    #    return jsonify(errors), 400
    orders = {"orders": []}
    for order in import_data['data']:
        newCourier = Courier(updated_at=datetime.now(), courier_id=order["order_id"],
                             weight=order["weight"], region=order["region"],
                             delivery_hours=pickle.dumps(order["working_hours"]))
        # TODO: sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: orders.order_id
        db_session.add(newCourier)
        orders["orders"].append({'id': order['orders_id']})
    db_session.commit()
    return jsonify(orders), 200


@app.route('/orders/assign', methods=['POST'])
def post_orders_assign():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')
    import_data = request.get_json()
    # TODO:errors = validate_orders(import_data)
    # if errors:
    #    return jsonify(errors), 400
    courier = Courier.query.filter_by(courier_id=import_data["courier_id"]).first()
    if not courier:
        raise BadRequest('incorrect id')
    maxweight = 10
    if courier.courier_type == "bike":
        maxweight = 15
    elif courier.courier_type == "car":
        maxweight = 50
    regions = pickle.loads(courier.regions)
    orders = Order.query.filter(Order.assign_time is None, Order.weight <= maxweight, Order.region in regions)
    # TODO: datetime check
    response = {"orders": [], "assign_time": ""}
    for order in orders:
        order.assign_time = datetime.now()
        order.courier_id = courier.courier_id
        response["orders"].append({'id': order['orders_id']})
    response["assign_time"] = "{}-{}-{}T{}:{}.{}Z".format(*[_ for _ in datetime.now().timetuple()][:6])
    db_session.commit()
    return jsonify(response), 200


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def update_couriers(courier_id):
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')
    import_data = request.get_json()
    errors = validate_patch_courier(import_data)
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
        print(courier.__dict__[key])
        if key in ["regions", "working_hours"]:
            json_courier[key] = pickle.loads(courier.__dict__[key])
        else:
            json_courier[key] = courier.__dict__[key]
    courier.updated_at = datetime.now()
    db_session.commit()
    # TODO: update orders
    return jsonify(json_courier), 200


@app.route('/')
@app.route('/index/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'


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
