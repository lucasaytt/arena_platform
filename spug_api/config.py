from pytz import timezone
import os

DEBUG = True
TIME_ZONE = timezone('Asia/Shanghai')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://hive_user:J2q1mbVBRMSHvucC@cn-bdp-mysql01.corp.cootek.com/tensorflow'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

DOCKER_REGISTRY_SERVER = 'localhost:5000'
DOCKER_REGISTRY_AUTH = {'username': 'user', 'password': 'password'}