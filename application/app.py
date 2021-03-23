import os
from datetime import datetime

from flask import Flask, request, Response, jsonify
from werkzeug.exceptions import BadRequest

from database import Courier, db_session, init_db
from validator import validate_couriers
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
