import mongoengine
from django.conf import settings


def connect_mongodb():
    if not mongoengine.connection._connections:
        mongoengine.connect(
            db=settings.MONGODB_DB,
            host=settings.MONGODB_URI,
            alias="default",
        )
