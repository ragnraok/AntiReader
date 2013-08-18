from flask import Flask
from antireader.logger import init_task_logger
from antireader.database import db

def init_task_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    db.init_app(app)
    db.app = app
    app.debug = app.config['DEBUG']
    init_task_logger(app)

    return app

task_app = init_task_app()
