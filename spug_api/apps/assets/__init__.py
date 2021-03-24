from apps.assets import host


def register_blueprint(app):
    app.register_blueprint(host.blueprint, url_prefix='/assets/hosts')
