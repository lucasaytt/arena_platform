from apps.account.models import User
from public import app
from flask import Blueprint, request, redirect, url_for, safe_join, send_from_directory
from collections import defaultdict
from urllib.parse import urlencode
import requests
import json
import base64
from libs.tools import json_response, JsonParser
from apps.index import config


blueprint = Blueprint(__name__, __name__)
login_limit = defaultdict(int)




@blueprint.route('/<any(css, img, js, sound):folder>/<path:filename>')
def toplevel_static(folder, filename):
    filename = safe_join(folder, filename)
    cache_timeout = app.get_send_file_max_age(filename)
    return send_from_directory(app.static_folder, filename,
                               cache_timeout=cache_timeout)


@blueprint.route('/')
def index(folder, filename):
    app.send_static_file("index.html")