from public import db
from libs.model import ModelMixin
from apps.system.models import NotifyWay
from sqlalchemy import func, text


class Image(db.Model, ModelMixin):
    __tablename__ = 'deploy_images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    desc = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, server_default=func.now(), comment='创建时间')
    # onupdate设置自动更改
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                            comment='修改时间')

    def __repr__(self):
        return '<Image %r>' % self.name


