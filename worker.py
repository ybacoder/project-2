# copied from https://devcenter.heroku.com/articles/python-rq


import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

def queue(func):
    def queued_func(*args, **kwargs):
        return Queue(connection=conn).enqueue(
            lambda args, kwargs: func(*args, **kwargs),
            "http://heroku.com"
        )
    return queued_func

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()