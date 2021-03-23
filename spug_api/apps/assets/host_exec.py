from flask import Blueprint, request
from apps.assets.models import Host
from libs.tools import json_response, JsonParser, Argument, QueuePool
from libs.ssh import ssh_exec_command_with_stream, get_ssh_client
from libs.decorators import require_permission
from threading import Thread
import uuid

blueprint = Blueprint(__name__, __name__)


@blueprint.route('/exec_command/<string:token>', methods=['DELETE'])
@require_permission('assets_host_exec')
def exec_delete(token):
    q = QueuePool.get_queue(token)
    if q:
        q.destroy()
    return json_response()

