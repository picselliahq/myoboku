from http import HTTPStatus
from typing import Any


class PicselliaAPIException(Exception):
    def __init__(
        self, message: str, status: int, detail: list = None, *args: Any, **kwargs: Any
    ) -> None:
        self.message = message
        self.status = status
        self.detail = detail if detail else []
        super().__init__(*args)


class UnauthorizedException(PicselliaAPIException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="Unauthorized", status=HTTPStatus.UNAUTHORIZED, *args, **kwargs
        )


class ForbiddenException(PicselliaAPIException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="Insufficient rights", status=HTTPStatus.FORBIDDEN, *args, **kwargs
        )


class BadRequestException(PicselliaAPIException):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            message="Bad Request", status=HTTPStatus.BAD_REQUEST, *args, **kwargs
        )
