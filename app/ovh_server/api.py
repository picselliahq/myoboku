from http import HTTPStatus
from uuid import UUID

from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from config.enums import JobRunStatus
from config.sdk import init_and_retrieve_client
from config.security.authentication import TokenAuthentication
from ovh_server.models import OVHJob
from ovh_server.schemas import JobInputSchema
from ovh_server.tasks import launch_job
from celery.worker.control import revoke


router = Router()


@router.post("/job", auth=TokenAuthentication())
@csrf_exempt
def init_job(request, payload: JobInputSchema):
    job = OVHJob(
        image=payload.image,
        env=parse_picsellia_env(payload.env),
        nb_cpu=payload.resources.cpu,
        nb_gpu=payload.resources.gpu,
        status=JobRunStatus.PENDING,
    )
    job.save()
    job_task = launch_job.delay(str(job.id))
    job.task_id = job_task.id
    job.save()
    return HTTPStatus.OK, {"id": str(job.id)}


@router.get("/job/{job_id}", auth=TokenAuthentication())
@csrf_exempt
def get_job(request, job_id: UUID):
    job = OVHJob.objects.filter(id=job_id)
    if job.exists():
        job = job.first()
        response = {"status": {"state": job.status}}
        return HTTPStatus.OK, response
    else:
        response = {"status": {"state": JobRunStatus.FAILED}}
        return HTTPStatus.OK, response


@router.get("/job/{job_id}/log", auth=TokenAuthentication())
@csrf_exempt
def get_job(request, job_id: UUID):
    job = OVHJob.objects.filter(id=job_id)
    if job.exists():
        return HTTPStatus.OK, b"log1\nlog2\n"
    else:

        return HTTPStatus.OK, b""


@router.put("/job/{job_id}/kill", auth=TokenAuthentication())
@csrf_exempt
def terminate_job(request, job_id: UUID):
    job = OVHJob.objects.get(id=job_id)
    revoke(job.task_id, terminate=True)
    job.status = JobRunStatus.KILLED
    job.save()
    return HTTPStatus.OK


def parse_picsellia_env(input_env: list) -> dict:
    env_dict: dict = {}
    for env_var in input_env:
        env_dict[env_var["name"]] = env_var["value"]
    return env_dict
