import os
from datetime import datetime
from flask import Flask, request, Response, jsonify
from werkzeug.exceptions import BadRequest
from database import Courier, db_session, init_db, Order
from validator import Validator
import pickle

app = Flask(__name__)
app.debug = True
validator = Validator()


@app.route('/couriers', methods=['POST'])
def post_couriers():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')

    import_data = request.get_json()
    errors = validator.couriers(import_data)
    if errors:
        return jsonify(errors), 400

    couriers = {'couriers': []}
    for courier in import_data['data']:
        new_courier = Courier(updated_at=datetime.now(), courier_id=courier['courier_id'],
                              courier_type=courier['courier_type'],
                              regions=courier['regions'],
                              working_hours=courier['working_hours'])
        # TODO: sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: couriers.courier_id
        # TODO не понятно

        db_session.add(new_courier)
        couriers['couriers'].append({'id': courier['courier_id']})
    db_session.commit()
    return jsonify(couriers), 201


@app.route('/orders', methods=['POST'])
def post_orders():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')

    import_data = request.get_json()
    errors = validator.orders(import_data)
    if errors:
        return jsonify(errors), 400

    orders = {'orders': []}
    for order in import_data['data']:
        new_order = Order(updated_at=datetime.now(), order_id=order['order_id'],
                          weight=order['weight'], region=order['region'],
                          delivery_hours=order['delivery_hours'])
        # TODO: sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: orders.order_id
        db_session.add(new_order)
        orders['orders'].append({'id': order['order_id']})
    db_session.commit()
    return jsonify(orders), 201


@app.route('/orders/assign', methods=['POST'])
def post_orders_assign():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')

    import_data = request.get_json()
    errors = validator.orders_assign(import_data)
    if errors:
        return jsonify(errors), 400
    
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
        print(courier.__dict__[key])
        if key in ["regions", "working_hours"]:
            json_courier[key] = pickle.loads(courier.__dict__[key])
        else:
            json_courier[key] = courier.__dict__[key]
    courier.updated_at = datetime.now()
    db_session.commit()
    # TODO: update orders
    return jsonify(json_courier), 200


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
