from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)


@app.route('/couriers', methods=['POST'])
def post_couriers():
    if not request.is_json:
        raise BadRequest('Content-Type must be application/json')

    import_data = request.get_json()



@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
