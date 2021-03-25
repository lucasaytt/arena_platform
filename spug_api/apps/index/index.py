from apps.account.models import User
from apps.assets.models import Host
from apps.schedule.models import Job
from flask import Blueprint
from flask import Flask
app = Flask(__name__, static_url_path='')


blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
