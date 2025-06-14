import os
from celery import Celery, Task
from src.config import settings
import time

_user = os.environ.get("RABBITMQ_DEFAULT_USER")
_password = os.environ.get("RABBITMQ_DEFAULT_PASS")

if not _user or not _password:
    raise ValueError(
        "RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS environment variables must be set."
    )

app = Celery(
    "tasks",
    broker=f"pyamqp://{_user}:{_password}@rabbitmq//",
    backend="db+" + str(settings.SQLALCHEMY_DATABASE_URI),
)

app.conf.update(
    task_track_started=True,
)

@app.task(bind=True)
def add(self: Task, x, y):
    time.sleep(30)  # Simulate a long-running task
    return x + y
