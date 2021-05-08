#!/usr/bin/env python
import django

from django.conf import settings
from django.core.management import call_command

app_name = 'django_web_analytics'
settings.configure(DEBUG=True,
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        app_name,
    ),
)

django.setup()
call_command('makemigrations', app_name)
