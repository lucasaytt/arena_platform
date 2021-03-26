from apps.account.models import User
from public import app
from flask import Blueprint, request, redirect, url_for
from collections import defaultdict
from urllib.parse import urlencode
import requests
import json
import base64
from libs.tools import json_response, JsonParser


blueprint = Blueprint(__name__, __name__)
login_limit = defaultdict(int)

sso_params = {
  "cootek.authorize": "https://idcsso.corp.cootek.com/adfs/oauth2/authorize/",
  "cootek.token": "https://idcsso.corp.cootek.com/adfs/oauth2/token",
  "cootek.logout": "https://idcsso.corp.cootek.com/adfs/oauth2/logout",
  "cootek.client-id": "a6e7edae-e3b8-43fd-92bc-f6208368b8be",
  "cootek.client-secret": "E4wjVfZeN_YoUA16GvyrV5SmwC7oplmsY20p24ru",
}

authorize_params = {
    "response_type": "code",
    "client_id": "a6e7edae-e3b8-43fd-92bc-f6208368b8be",
    "redirect_uri": "https://tensorflow-test.cootekos.com/index",
}

token_params = {
    "grant_type": "authorization_code",
    "code": "",
    "client_id": "a6e7edae-e3b8-43fd-92bc-f6208368b8be",
    "redirect_uri": "https://tensorflow-test.cootekos.com/index",
    "client_secret": "E4wjVfZeN_YoUA16GvyrV5SmwC7oplmsY20p24ru",
}

logout_params = {
    "client_id": "a6e7edae-e3b8-43fd-92bc-f6208368b8be",
}


@blueprint.route('/', methods=['GET'])
@blueprint.route('', methods=['GET'])
def login():
    code = request.values.get("code")
    if code is None:
        # Authorize the client from SSO, redirect as a query with "code"
        sl = "?".join([sso_params.get("cootek.authorize"), urlencode(authorize_params)])
        return redirect(sl)
    else:
        token_params.update({"code": code})


@blueprint.route('/get_user_info', methods=['GET'])
def sso_get_user_info():
    code = request.values.get("code")
    if code is None:
        # Authorize the client from SSO, redirect as a query with "code"
        sl = "?".join([sso_params.get("cootek.authorize"), urlencode(authorize_params)])
        return redirect(sl)
    else:
        token_params.update({"code": code})
    try:
        # Request access_token and id_token from SSO
        # Username and password required.
        ret = requests.post(sso_params.get("cootek.token"), data=token_params)
    except Exception:
        import traceback
        print('something wrong when request token')
        traceback.print_exc()
        sl = "?".join([sso_params.get("cootek.authorize"), urlencode(authorize_params)])
        return redirect(sl)

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
        return json_response({"username":username,"token":sid})


@blueprint.route('/logout', methods=['GET'])
def logout():
        sl = "?".join([sso_params.get("cootek.logout"), urlencode(logout_params)])
        return redirect(sl)