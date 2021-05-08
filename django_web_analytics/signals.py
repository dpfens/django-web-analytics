from django.db.models import signals
from django.contrib.auth import get_user_model
from django_web_analytics import models


User = get_user_model()


def create_user_settings(sender, instance, created, **kwargs):
    if created:
        models.Privacy.objects.create(user=instance)


signals.post_save.connect(create_user_settings, sender=User)
