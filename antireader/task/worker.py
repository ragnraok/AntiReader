from update_feed import update_feed
#from antireader.app import task_app as app
from app import task_app as app
from rq import Connection, Queue, Worker

import os
import redis

QUEUE_NAME = "antireader_queue"

redis_url = app.config['REDIS_URL']
conn = redis.from_url(redis_url)

queue = Queue(QUEUE_NAME, connection=conn)


def add_update_task(site_id):
    app.logger.info('update task for id %d enqueue' % site_id)
    queue.enqueue(update_feed, site_id)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(queues=queue)
        worker.work()
