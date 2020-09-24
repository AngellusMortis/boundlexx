import djclick as click

from django_celery_results.models import TaskResult


@click.command()
def command():
    TaskResult.objects.filter(status="STARTED").delete()
