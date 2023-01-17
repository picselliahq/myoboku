from __future__ import absolute_import, unicode_literals

import os

import django
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()  # Hack to make django_celery_results work when calling celery CLI
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
