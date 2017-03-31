# Create your tasks here
from __future__ import absolute_import, unicode_literals
# from celery import Task, shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger


log = get_task_logger(__name__)


@task(name="add")
def add(a, b):
    """sends an email when feedback form is filled successfully"""
    log.info("Adding ")
    return a + b
