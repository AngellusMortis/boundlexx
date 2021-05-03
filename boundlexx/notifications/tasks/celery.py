from config.celery_app import app


@app.task
def error_task_celery():
    raise Exception("test")
