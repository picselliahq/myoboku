import logging
from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist
from docker.errors import APIError
from ninja import NinjaAPI

from config.authentication import TokenAuthentication
from config.renderer import ORJSONRenderer
from myoboku.api import router as v1_router
from myoboku.exceptions import PicselliaAPIException

logger = logging.getLogger(__name__)

api = NinjaAPI(
    title="Myoboku",
    csrf=False,
    auth=TokenAuthentication(),
    version="1",
    urls_namespace="api",
    renderer=ORJSONRenderer(),
    description="Picsellia API",
    docs_url="/docs",
)

api.add_router("v1", v1_router)


@api.exception_handler(PicselliaAPIException)
def api_handle_picsellia_api_exception(request, exc: PicselliaAPIException):
    return api.create_response(
        request,
        {"message": exc.message, "detail": exc.detail},
        status=exc.status,
    )


@api.exception_handler(ObjectDoesNotExist)
def api_handle_object_not_found(request, exc):
    return api.create_response(
        request,
        {"message": "Object not found", "detail": str(exc)},
        status=HTTPStatus.NOT_FOUND,
    )


@api.exception_handler(Exception)
def api_handle_exception(request, exc):
    logger.error(f"internal error on {request.path}", exc_info=exc)
    return api.create_response(
        request,
        {"message": "Something went wrong"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


@api.exception_handler(APIError)
def api_handle_docker_api_error(request, exc):
    logger.error(
        f"something went wrong while contacting docker server on {request.path}",
        exc_info=exc,
    )
    return api.create_response(
        request,
        {"message": "Something went wrong with docker daemon"},
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
