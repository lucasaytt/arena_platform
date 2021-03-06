from apps.account.models import User
from public import app
from flask import Blueprint, request, redirect, g
from collections import defaultdict
from urllib.parse import urlencode
import requests
import json
import base64
from libs.tools import json_response
from apps.index import config
import uuid
import time
from flask_login import LoginManager,login_user,current_user,login_required


blueprint = Blueprint(__name__, __name__)
login_limit = defaultdict(int)


@blueprint.route('/', methods=['GET'])
@blueprint.route('', methods=['GET'])
def login():
    code = request.values.get("code")
    if code is None:
        # Authorize the client from SSO, redirect as a query with "code"
        sl = "?".join([config.sso_params.get("cootek.authorize"), urlencode(config.authorize_params)])
        return redirect(sl)
    else:
        config.token_params.update({"code": code})
        ret = requests.post(config.sso_params.get("cootek.token"), data=config.token_params)
        token = json.loads(ret.text)
        if "access_token" in token and "id_token" in token:
            # Analyse username from id_token
            user_info = token['id_token'].split(".")[1]
            missing_padding = 4 - len(user_info) % 4
            if missing_padding:
                user_info += '=' * missing_padding
            temp_user_info = base64.b64decode(user_info)
            user_info = json.loads(bytes.decode(temp_user_info))

            username = user_info['upn'].split("@")[0]
            sid = user_info['sid'].split("@")[0]
            token = uuid.uuid4().hex
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User()
                user.username = username
                user.access_token = token
                user.token_expired = time.time() + 8 * 60 * 60
                user.save()
            login_user(user)
            return app.send_static_file('index.html')
        else:
            sl = "?".join([config.sso_params.get("cootek.authorize"), urlencode(config.authorize_params)])
            return redirect(sl)


@blueprint.route('/user', methods=['GET'])
def sso_get_user_info():
    return json_response({"username": current_user.username, "bu": "ad"})


@blueprint.route('/logout', methods=['GET'])
def logout():
    if login_required:
        sl = "?".join([config.sso_params.get("cootek.logout"), urlencode(config.logout_params)])
        return redirect(sl)
    else:
        return redirect("/index")