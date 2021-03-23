from public import app
from flask import Blueprint
from libs.tools import json_response, JsonParser
from libs.utils import Registry
from apps.deploy.models import Image
from libs.decorators import require_permission

blueprint = Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET'])
@require_permission('publish_image_view | publish_app_add')
def get():
    return json_response(Image.query.all())


@blueprint.route('/add', methods=['POST'])
@require_permission('publish_image_add')
def add():
    form, error = JsonParser('name','desc','tag').parse()
    if error is None:
        image = Image.query.filter_by(name=form.name).first()
        if image:
            return json_response(message='该镜像名字已经存在。')

        tag = form.pop('tag')
        res = Image(**form).save()

        if  res:
            return json_response()

        return json_response(message='添加镜像失败,请稍后再试!')
    return json_response(message=error)


@blueprint.route('/<int:img_id>', methods=['PUT'])
@require_permission('publish_image_edit')
def put(img_id):
    form, error = JsonParser('desc').parse()
    if error is None:
        image = Image.query.get_or_404(img_id)
        image.update(**form)
        return json_response()
    return json_response(message=error)


@blueprint.route('/<int:img_id>', methods=['DELETE'])
@require_permission('publish_image_del')
def delete(img_id):
    image = Image.query.get_or_404(img_id)
    image.delete()
    return json_response()
