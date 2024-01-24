from typing import Any, Optional

from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer

from myoboku.exceptions import UnauthorizedException


class TokenAuthentication(HttpBearer):
    def authenticate(self, request: HttpRequest, token: Optional[str]) -> Optional[Any]:
        if not token or token != settings.AUTHENTICATION_TOKEN:
            raise UnauthorizedException()

        return True
