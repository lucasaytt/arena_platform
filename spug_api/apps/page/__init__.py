from apps.page import page


def register_blueprint(app):
    app.register_blueprint(page.blueprint)
