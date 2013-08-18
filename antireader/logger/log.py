import logging
from logging.handlers import RotatingFileHandler

def init_logger(app):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=100000,
            backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    #app.logger.addHandler(stream_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.propagate = False

def init_task_logger(app):
    logger = logging.getLogger('apscheduler.scheduler')
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')

    file_handler = RotatingFileHandler(app.config['TASK_LOG_FILE'], maxBytes=100000,
            backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    #app.logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
