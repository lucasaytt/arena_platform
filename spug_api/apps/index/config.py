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