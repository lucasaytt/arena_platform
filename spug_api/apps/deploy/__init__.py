from apps.deploy import image

def register_blueprint(app):
    app.register_blueprint(image.blueprint, url_prefix='/deploy/images')

