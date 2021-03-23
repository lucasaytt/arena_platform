from public import db
from libs.model import ModelMixin
from apps.system.models import NotifyWay


class Image(db.Model, ModelMixin):
    __tablename__ = 'deploy_images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    desc = db.Column(db.String(255))

    def __repr__(self):
        return '<Image %r>' % self.name


