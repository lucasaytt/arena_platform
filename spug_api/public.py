from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config
from flask_login import login_manager


app = Flask(__name__, static_url_path='')
login_manager.LoginManager.init_app(app)
app.config.from_object(config)
db = SQLAlchemy(app)
