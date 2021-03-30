from flask import Blueprint, request
from apps.assets.models import Host, HostExtend
from libs.tools import json_response, JsonParser, Argument
from apps.setting import utils, Setting
from libs import ssh
from libs.utils import DockerClient, DockerException
import math
from public import db
from apps.assets.utils import excel_parse
import paramiko
import re

blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
def get():
    form, error = JsonParser(Argument('page', type=int, default=1, required=False),
                             Argument('pagesize', type=int, default=10, required=False),
                             Argument('host_query', type=dict, default={}), ).parse(request.args)
    if error is None:
        host_data = Host.query
        if form.page == -1:
            return json_response({'data': [x.to_json() for x in host_data.all()], 'total': -1})
        if form.host_query.get('name_field'):
            host_data = host_data.filter(Host.name.like('%{}%'.format(form.host_query['name_field'])))
        if form.host_query.get('zone_field'):
            host_data = host_data.filter_by(zone=form.host_query['zone_field'])

        result = host_data.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
        return json_response({'data': [x.to_json() for x in result], 'total': host_data.count()})
    return json_response(message=error)


@blueprint.route('/', methods=['POST'])
def post():
    form, error = JsonParser('name', 'type', 'zone', 'docker_uri', 'ssh_ip', 'ssh_port',
                             Argument('desc', nullable=True, required=False)).parse()
    if error is None:
        host = Host(**form)
        host.save()
        return json_response(host)
    return json_response(message=error)


@blueprint.route('/<int:host_id>', methods=['DELETE'])
def delete(host_id):
    host = Host.query.get_or_404(host_id)
    host.delete()
    return json_response()


@blueprint.route('/<int:host_id>', methods=['PUT'])
def put(host_id):
    form, error = JsonParser('name', 'type', 'zone', 'docker_uri', 'ssh_ip', 'ssh_port',
                             Argument('desc', nullable=True, required=False)).parse()
    if error is None:
        host = Host.query.get_or_404(host_id)
        host.update(**form)
        return json_response(host)
    return json_response(message=error)


@blueprint.route('/<int:host_id>/valid', methods=['GET'])
def get_valid(host_id):
    cli = Host.query.get_or_404(host_id)
    if not Setting.has('ssh_private_key'):
        utils.generate_and_save_ssh_key()
    if ssh.ssh_ping(cli.ssh_ip, cli.ssh_port):
        try:
            sync_host_info(host_id, cli.docker_uri)
        except DockerException:
            return json_response(message='docker fail')
    else:
        return json_response(message='ssh fail')
    return json_response()


@blueprint.route('/<int:host_id>/valid', methods=['POST'])
def post_valid(host_id):
    form, error = JsonParser(Argument('secret', help='请输入root用户的密码！')).parse()
    if error is None:
        cli = Host.query.get_or_404(host_id)
        ssh.add_public_key(cli.ssh_ip, cli.ssh_port, form.secret)
        if ssh.ssh_ping(cli.ssh_ip, cli.ssh_port):
            try:
                sync_host_info(host_id, cli.docker_uri)
            except DockerException:
                return json_response(message='获取扩展信息失败，请检查docker是否可以正常连接！')
        else:
            return json_response(message='验证失败！')
    return json_response(message=error)


@blueprint.route('/<int:host_id>/extend/', methods=['GET'])
def get_extend(host_id):
    host_extend = HostExtend.query.filter_by(host_id=host_id).first()
    return json_response(host_extend)


@blueprint.route('/zone/', methods=['GET'])
def fetch_groups():
    zones = db.session.query(Host.zone.distinct().label('zone')).all()
    return json_response([x.zone for x in zones])


@blueprint.route('/import', methods=['POST'])
def host_import():
    data = excel_parse()
    if data:
        index_map = {key: index for index, key in enumerate(data.keys())}
        for row in zip(*data.values()):
            print(row)
            Host(
                name=row[index_map['主机名称']],
                desc=row[index_map['备注信息']],
                type=row[index_map['主机类型']],
                zone=row[index_map['所属区域']],
                docker_uri=row[index_map['Docker连接地址']],
                ssh_ip=row[index_map['SSH连接地址']],
                ssh_port=row[index_map['SSH端口']],
            ).add()
        db.session.commit()
        return json_response(data='导入成功')


def sync_host_info(host_id, uri):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli = Host.query.get_or_404(host_id)
    ssh.connect(cli.ssh_ip, username='hadoop', password='')

    stdin, stdout, stderr = ssh.exec_command('cat /proc/meminfo')
    str_out = stdout.read().decode()
    str_total = re.search('MemTotal:.*?\n', str_out).group()
    memory = re.search('\d+', str_total).group()

    str_free = re.search('MemAvailable:.*?\n', str_out).group()

    operate_system = 'centos';
    HostExtend.upsert({'host_id': host_id}, host_id=host_id, operate_system=operate_system, memory=memory, cpu='')
    return True
