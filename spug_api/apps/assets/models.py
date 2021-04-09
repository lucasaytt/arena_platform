from public import db
from libs.model import ModelMixin
import datetime
from sqlalchemy import func, text


class Host(db.Model, ModelMixin):
    __tablename__ = 'assets_hosts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(255))
    type = db.Column(db.String(50))
    zone = db.Column(db.String(50))
    ssh_ip = db.Column(db.String(32))
    ssh_port = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, server_default=func.now(), comment='创建时间')
    # onupdate设置自动更改
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                            comment='修改时间')

    def __repr__(self):
        return '<Host %r>' % self.name


class HostExtend(db.Model, ModelMixin):
    __tablename__ = 'assets_hosts_extend'

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('assets_hosts.id'))
    operate_system = db.Column(db.String(64))
    memory = db.Column(db.SmallInteger)
    cpu_core = db.Column(db.SmallInteger)
    avaliable_mem = db.Column(db.SmallInteger)
    avaliable_core = db.Column(db.SmallInteger)
    hosts = db.relationship(Host, backref=db.backref('host'))
    create_time = db.Column(db.DateTime, server_default=func.now(), comment='创建时间')
    # onupdate设置自动更改
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                            comment='修改时间')