from public import db
from libs.model import ModelMixin
from sqlalchemy import text, func
from flask_login import UserMixin


class User(db.Model, ModelMixin, UserMixin):
    __tablename__ = 'account_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    is_supper = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    access_token = db.Column(db.String(32))
    token_expired = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, server_default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                            comment='修改时间')
