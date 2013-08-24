import os
import json

HERE = os.path.dirname(__file__)
DEBUG = True
DATABASE_NAME = 'antireader.db'
ADMIN_NAME = "antireader"
ADMIN_PASSWORD = "antireader"
LOG_FILE = "antireader.log"
TASK_LOG_FILE = "antireader_task.log"
SECRET_KEY = "PtV9ua4oSBknM5GbTLNQ"
DEFAULT_ARTICLE_SHOW_NUM = 30
PER_PAGE_ARTICLE_NUM = 10
SQLALCHEMY_ECHO = False

"""
database setting
"""
SQLALCHEMY_DATABASE_URI = "sqlite:////" + HERE + "/" + DATABASE_NAME
REDIS_URL = 'redis://localhost:6379'

if DEBUG:
    pass
else:
    pass
