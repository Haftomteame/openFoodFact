from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_jwt_token(user: User) -> str:
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed("Token expiré.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed("Token invalide.") from exc


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header[len(self.keyword) + 1 :].strip()
        if not token:
            return None

        payload = decode_jwt_token(token)
        user = User.objects(id=payload["user_id"]).first()
        if not user:
            raise AuthenticationFailed("Utilisateur introuvable.")

        return (user, token)
