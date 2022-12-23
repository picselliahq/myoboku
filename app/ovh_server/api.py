from http import HTTPStatus

from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from config.security.authentication import TokenAuthentication
from ovh_server.schemas import JobInputSchema


router = Router()


@router.post("/job", auth=TokenAuthentication())
@csrf_exempt
def add(request, payload: JobInputSchema):
    print(payload)
    return HTTPStatus.OK
