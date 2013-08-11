from flask import Flask
from database import db

from antireader.logger import init_logger, init_task_logger

def init_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    app.debug = app.config['DEBUG']

    init_logger(app)

    return app

app = init_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
