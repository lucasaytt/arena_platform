from flask import Blueprint, request, abort
from libs.tools import json_response, JsonParser, Argument, human_diff_time
from apps.schedule.scheduler import scheduler
from apps.assets.models import Host
from apps.schedule.models import Job,JobSchedule
from datetime import datetime
from public import db
import uuid
from threading import Thread
from libs.tools import json_response, JsonParser, Argument, QueuePool
from libs.ssh import ssh_exec_command_with_stream, get_ssh_client


blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
def get():
    form, error = JsonParser(
        Argument('page', type=int, default=1, required=False),
        Argument('pagesize', type=int, default=10, required=False),
        Argument('job_group', type=str, required=False),).parse(request.args)

    if error is None:
        if form.job_group:
            job = Job.query.filter_by(group=form.job_group).order_by(Job.enabled.desc())
        else:
            job = Job.query.order_by(Job.enabled.desc())

        total = job.count()
        job_data = job.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
        jobs = [x.to_json() for x in job_data]
        now = datetime.now()
        for job in jobs:
            if not job['enabled']:
                job['next_run_time'] = '未启用'
            elif str(job['id']) in scheduler.jobs:
                next_run_time = scheduler.jobs[str(job['id'])].next_run_time
                if next_run_time is None:
                    job['next_run_time'] = '已过期'
                else:
                    job['next_run_time'] = human_diff_time(next_run_time.replace(tzinfo=None), now)
            elif job['trigger'] == 'date' and now > datetime.strptime(job['trigger_args'], '%Y-%m-%d %H:%M:%S'):
                job['next_run_time'] = '已过期'
            else:
                job['next_run_time'] = '异常'
        return json_response({'data': jobs, 'total': total})
    return json_response({'message': error})


@blueprint.route('/<int:job_id>', methods=['GET'])
def get_single_job(job_id):
    job = Job.query.filter_by(id=job_id).first()
    if job == None:
        error = "no record"
        return json_response(message=error)
    else:
        return json_response({'data': job.to_json(), 'total': 1})


@blueprint.route('/get_schedule_instance', methods=['GET'])
def get_schedule():
    form, error = JsonParser(
        Argument('page', type=int, default=1, required=False),
        Argument('pagesize', type=int, default=10, required=False),
        Argument('job_group', type=str, required=False),
        Argument('job_name', type=str, required=False),
        Argument('job_id', type=int, required=False),).parse(request.args)

    if error is None:
        job = db.session.query(JobSchedule)
        if form.job_group:
            job = JobSchedule.query.filter_by(group=form.job_group).order_by(JobSchedule.update_time.desc())
        if form.job_name:
            job = job.filter(JobSchedule.job_name.like("%" + form.job_name + "%"))
        if form.job_id:
            job = job.filter_by(job_id=form.job_id)

        job = job.order_by(JobSchedule.update_time.desc())

        total = job.count()
        job_data = job.limit(form.pagesize).offset((form.page - 1) * form.pagesize).all()
        jobs = [x.to_json() for x in job_data]
        return json_response({'data': jobs, 'total': total})
    return json_response(message=error)


@blueprint.route('/get_instance_log', methods=['GET'])
def get_instance_log():
    form, error = JsonParser(
        Argument('task_instance_name', type=str, required=True),).parse(request.args)

    if error is None:
        try:
            path = '/tensorflow/{task_instance_name}/chief.log'.format(task_instance_name=form.task_instance_name)
            log = open(path, 'r', encoding='UTF-8').read()
            # 成功获取到md文件内容啦
            return json_response({'data': log})
        except OSError as reason:
            error = '读取文件出错了T_T,出错原因是%s' % str(reason)
    return json_response(message=error)


@blueprint.route('/kill_job', methods=['POST'])
def kill_job():
    form, error = JsonParser(
        'job_schedule_name',
        'kill_user',
        'hosts_id',
        'id',
        Argument('command', type=str, default='bash /tensorflow/arena_stop/arena_job_kill.sh', required=False),
       ).parse()
    print("hosts_id" + str(form.hosts_id) + "  command:" + form.command)
    # 这里操作是ssh后初始化环境变量
    new_command = "source /etc/profile &&. /etc/profile && " + form.command + " " + form.kill_user + " " + \
                  form.job_schedule_name + " " + str(id)
    if error is None:
        ip_list = Host.query.filter(Host.id.in_(tuple(form.hosts_id))).all()
        token = uuid.uuid4().hex
        q = QueuePool.make_queue(token, len(ip_list))
        for h in ip_list:
            print(h.ssh_ip)
            Thread(target=hosts_exec, args=(q, h.ssh_ip, 'ad_user', h.ssh_port, new_command)).start()
        return json_response(token)
    return json_response(message=error)


@blueprint.route('/', methods=['POST'])
def post():
    form, error = JsonParser(
        'bu_name', 'owner', 'name', 'group', 'desc', 'command_user', 'command', 'targets',
        Argument('bu_name', default='ad_user'),
        Argument('owner', default='rui.lu'),
        Argument('command_user', default='root')
    ).parse()

    job_id = ''
    if error is None:
        # 增加任务名字重复判断
        exist_job = Job.query.filter_by(name=form.name)
        if exist_job.count() > 0:
            job_create_error = form.name + '任务名已经存在!!!'
            return json_response({'message': job_create_error})
        else:
            job = Job(**form).save()
            job_id = job.id
    return json_response({'message': error, 'id': job_id})


@blueprint.route('/<int:job_id>', methods=['PUT'])
def put(job_id):
    form, error = JsonParser(
        'bu_name', 'owner', 'name', 'group', 'desc', 'command', 'targets',
        Argument('bu_name', default='ad_user'), Argument('owner', default='rui.lu'),
        Argument('command_user', default='ad_user')
    ).parse()
    if error is None:
        job = Job.query.get_or_404(job_id)
        job.update(**form)
    return json_response(message=error)


@blueprint.route('/<int:job_id>/trigger', methods=['POST'])
def set_trigger(job_id):
    form, error = JsonParser(
        Argument('trigger', filter=lambda x: x in ['cron', 'date', 'interval'], help='错误的调度策略！'),
        Argument('trigger_args')
    ).parse()
    if error is None:
        if not scheduler.valid_job_trigger(form.trigger, form.trigger_args):
            return json_response(message='数据格式校验失败！')
        job = Job.query.get_or_404(job_id)
        if job.update(**form):
            scheduler.update_job(job)
    return json_response({'message': error})


@blueprint.route('/<int:job_id>/switch', methods=['POST', 'DELETE'])
def switch(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        if job.trigger is None:
            return json_response(message='请在 更多-设置触发器 中配置调度策略')
        job.update(enabled=True)
        command_trans = 'su -l ' + job.command_user + ' -c \'' + job.command+'\''
        print("===========", command_trans)
        if job.command_user == 'root':
            return json_response({'message': '静止使用root账户提交'})
        else:
            scheduler.add_job(job)
    elif request.method == 'DELETE':
        job.update(enabled=False)
        scheduler.remove_job(job.id)
    else:
        abort(405)
    return json_response()


@blueprint.route('/<int:job_id>', methods=['DELETE'])
def delete(job_id):
    job = Job.query.get_or_404(job_id)
    job.delete()
    scheduler.remove_job(job.id)
    return json_response()


@blueprint.route('/groups/', methods=['GET'])
def fetch_groups():
    apps = db.session.query(Job.group.distinct().label('group')).all()
    return json_response([x.group for x in apps])


@blueprint.route('/exec_command', methods=['POST'])
def exec_host_command():
    form, error = JsonParser('hosts_id', 'command').parse()
    print("hosts_id"+form.hosts_id+"  command:"+form.command)
    #这里操作是ssh后初始化环境变量
    new_command = "source /etc/profile &&. /etc/profile && "+form.command
    if error is None:
        ip_list = Host.query.filter(Host.id.in_(tuple(form.hosts_id))).all()
        token = uuid.uuid4().hex
        q = QueuePool.make_queue(token, len(ip_list))
        for h in ip_list:
            print(h.ssh_ip)
            Thread(target=hosts_exec, args=(q, h.ssh_ip, 'ad_user', h.ssh_port, new_command)).start()
        return json_response(token)
    return json_response(message=error)


def hosts_exec(q, ip, username, port, command):
    ssh_client = get_ssh_client(ip, username, port)
    q.destroyed.append(ssh_client.close)
    output = ssh_exec_command_with_stream(ssh_client, command)
    print("===============")
    print(output)
    for line in output:
        print(line)
        q.put({ip: line})
    print("===============")
    q.put({ip: '\n** 执行完成 **'})
    q.done()


@blueprint.route('/exec_command/<string:token>', methods=['DELETE'])
def exec_delete(token):
    q = QueuePool.get_queue(token)
    if q:
        q.destroy()
    return json_response()