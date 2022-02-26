from flask import Blueprint

v1_app = Blueprint('v1_app', import_name='views.v1', url_prefix='/')
v1_1_app = Blueprint('v1_1_app', import_name='views.v1_1', url_prefix='/v1_1')
v1_2_app = Blueprint('v1_2_app', import_name='views.v1_2', url_prefix='/v1_2')
v1_3_app = Blueprint('v1_3_app', import_name='views.v1_3', url_prefix='/v1_3')


all_blueprints = (
    v1_app,
    v1_1_app,
    v1_2_app,
    v1_3_app
)
