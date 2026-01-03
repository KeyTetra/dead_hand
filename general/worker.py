import os
import time
import random

from celery import Celery

app = Celery(
    'dead_hand',
broker='redis://localhost:6379',
backend='redis://localhost:6379'
)

@app.task
def random_number(max_value):
    time.sleep(5)
    return random.randint(0, max_value)