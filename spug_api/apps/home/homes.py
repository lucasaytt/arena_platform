from apps.account.models import User
from apps.assets.models import Host
from apps.schedule.models import Job
from flask import Blueprint
from libs.tools import json_response


blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
def get():
    user_total = User.query.count()
    host_total = Host.query.count()
    job_total = Job.query.count()

    data = {'user_total': user_total,
            'host_total': host_total,
            'job_total': job_total,
            'app_total': 0,
            }
    return json_response(data)
