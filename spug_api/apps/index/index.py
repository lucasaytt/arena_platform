
from public import app
from flask import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@blueprint.route('', methods=['GET'])
def index():
    return app.send_static_file('index.html')