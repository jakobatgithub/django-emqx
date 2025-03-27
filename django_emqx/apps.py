## django_emqx/apps.py

from django.apps import AppConfig


class DjangoEMQXConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_emqx'
    verbose_name = "Django EMQX"
