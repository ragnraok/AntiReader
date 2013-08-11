import os
import json

HERE = os.path.dirname(__file__)
DEBUG = True
DATABASE_NAME = 'antireader.db'
ADMIN_NAME = "antireader"
ADMIN_PASSWORD = "antireader"
LOG_FILE = "antireader.log"
SECRET_KEY = "PtV9ua4oSBknM5GbTLNQ"

"""
database setting
"""
SQLALCHEMY_DATABASE_URI = "sqlite:////" + HERE + "/" + DATABASE_NAME
REDIS_URL = 'redis://localhost:6379'

if DEBUG:
    SQLALCHEMY_ECHO = True
else:
    SQLALCHEMY_ECHO = False
