from apps.index import index


def register_blueprint(app):
    app.register_blueprint(index.blueprint, url_prefix='/index')
