from public import app
from config import DEBUG
from libs import middleware
from apps import deploy
from apps import assets
from apps import account
from apps import schedule
from apps import home
from apps import common
from apps import system
from apps import index
from flask_login import LoginManager
from apps.account.models import User


middleware.init_app(app)
account.register_blueprint(app)
deploy.register_blueprint(app)
assets.register_blueprint(app)
schedule.register_blueprint(app)
home.register_blueprint(app)
common.register_blueprint(app)
system.register_blueprint(app)
index.register_blueprint(app)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.login_message = u"invalid request return index page"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=DEBUG)
