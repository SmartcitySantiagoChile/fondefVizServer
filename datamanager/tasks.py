from celery import Celery

app = Celery('tasks', broker='redis://200.9.100.91:6379/0')

@app.task
def add(x, y):
    return x + y