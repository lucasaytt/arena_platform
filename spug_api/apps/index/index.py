from apps.account.models import User
from public import app
from flask import Blueprint, request, redirect, url_for
from collections import defaultdict
from urllib.parse import urlencode
import requests
import json
import base64
from libs.tools import json_response, JsonParser
import config


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
            return app.send_static_file('index.html')
        else:
            sl = "?".join([config.sso_params.get("cootek.authorize"), urlencode(config.authorize_params)])
            return redirect(sl)


@blueprint.route('/get_user_info', methods=['GET'])
def sso_get_user_info():
    code = request.values.get("code")
    if code is None:
        # Authorize the client from SSO, redirect as a query with "code"
        sl = "?".join([config.sso_params.get("cootek.authorize"), urlencode(config.authorize_params)])
        return redirect(sl)
    else:
        config.token_params.update({"code": code})
    try:
        # Request access_token and id_token from SSO
        # Username and password required.
        ret = requests.post(config.sso_params.get("cootek.token"), data=config.token_params)
    except Exception:
        import traceback
        print('something wrong when request token')
        traceback.print_exc()
        sl = "?".join([config.sso_params.get("cootek.authorize"), urlencode(config.authorize_params)])
        return redirect(sl)

    token = json.loads(ret.text)
    if "access_token" in token and "id_token" in token:
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
        # Analyse username from id_token
        user_info = token['id_token'].split(".")[1]
        missing_padding = 4 - len(user_info) % 4
        if missing_padding:
            user_info += '=' * missing_padding
        temp_user_info = base64.b64decode(user_info)
        user_info = json.loads(bytes.decode(temp_user_info))

        username = user_info['upn'].split("@")[0]
        sid = user_info['sid'].split("@")[0]
        return json_response({"username":username,"token":sid})


@blueprint.route('/logout', methods=['GET'])
def logout():
        sl = "?".join([sso_params.get("cootek.logout"), urlencode(logout_params)])
        return redirect(sl)