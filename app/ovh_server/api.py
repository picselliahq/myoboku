from http import HTTPStatus

from ninja import Router

from ovh_server.schemas import JobInputSchema


router = Router()


@router.post("/job")
def add(request, payload: JobInputSchema):
    print(payload)
    return HTTPStatus.OK
