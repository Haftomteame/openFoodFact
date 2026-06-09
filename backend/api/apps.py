from django.apps import AppConfig
from mongoengine import connect

from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        connect(
            db=settings.MONGODB_DB,
            host=settings.MONGODB_URI,
            alias="default",
        )
