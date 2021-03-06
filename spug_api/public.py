from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'tensorflow'
app.config.from_object(config)
db = SQLAlchemy(app)
