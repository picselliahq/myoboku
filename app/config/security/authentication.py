from typing import Any, Optional

from config.exceptions import UnauthorizedException
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja.security.apikey import APIKeyCookie
from userauth.models import Token


class TokenAuthentication(HttpBearer):
    def authenticate(self, request: HttpRequest, token: Optional[str]) -> Optional[Any]:
        if not token:
            raise UnauthorizedException()

        try:
            user_token: Token = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise UnauthorizedException()

        if not user_token.user.is_active:
            raise UnauthorizedException()

        request.user = user_token.user
        return user_token


class SessionAuthentication(APIKeyCookie):
    param_name: str = settings.SESSION_COOKIE_NAME

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if request.user.is_authenticated:
            return request.user

        raise UnauthorizedException()
