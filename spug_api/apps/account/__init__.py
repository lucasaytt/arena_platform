from apps.account import user


def register_blueprint(app):
    app.register_blueprint(user.blueprint, url_prefix='/account/users')
