import logging
from http import HTTPStatus
from threading import Thread
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from docker.errors import NotFound
from docker.models.resource import Model
from ninja import Router

from config import settings
from myoboku.exceptions import BadRequestException
from myoboku.external import docker_client
from myoboku.models import Job
from myoboku.schemas import (
    DockerContainerEnum,
    JobInput,
    JobLogsSchema,
    JobSchema,
    JobStatusSchema,
)

router = Router()

logger = logging.getLogger(__name__)


@router.get("/ping", response={HTTPStatus.OK: None}, operation_id="ping")
def ping(request):
    return HTTPStatus.OK, None


@router.post("/jobs", response={HTTPStatus.CREATED: JobSchema})
def launch_job(request, payload: JobInput):
    if _is_overwhelmed():
        raise BadRequestException(detail=["Myoboku is overwhelmed"])

    if payload.docker_connector_id:
        # TODO: Retrieve ids by
        # TODO: login to docker registry
        raise NotImplementedError()

    docker_client.ping()

    job = Job.objects.create(
        docker_image_name=payload.docker_image_name,
        docker_environment=payload.env,
        nb_cpu=payload.nb_cpu,
        nb_gpu=payload.nb_gpu,
        docker_connector_id=payload.docker_connector_id,
    )
    logger.info(f"Pulling with image {payload.docker_image_name}")

    docker_environment = [f"{key}={value}" for key, value in payload.env.items()]

    try:
        thread = Thread(
            target=_run_docker,
            args=(job.id, payload.docker_image_name, docker_environment),
        )
        thread.start()
    except Exception as e:
        logger.exception(
            f"Something went wrong while running {payload.docker_image_name}"
        )
        job.killed_at = timezone.now()
        job.save()
        raise BadRequestException(
            detail=[f"Docker image could not be run: {e!r}"]
        ) from e

    logger.info(f"Launching {job} with image {payload.docker_image_name}")
    return HTTPStatus.CREATED, job


@router.put("/jobs/{job_id}/kill", response={HTTPStatus.OK: JobSchema})
def kill_job(request, job_id: str):
    job = Job.objects.get(id=job_id)

    container = _get_container(job)

    with transaction.atomic():
        job.killed_at = timezone.now()
        job.save()
        container.kill()

    return HTTPStatus.OK, job


@router.get("/jobs/{job_id}", response={HTTPStatus.OK: JobSchema})
def get_job(request, job_id: str):
    return HTTPStatus.OK, Job.objects.get(id=job_id)


@router.get("/jobs/{job_id}/status", response={HTTPStatus.OK: JobStatusSchema})
def get_job_status(request, job_id: str):
    job = Job.objects.get(id=job_id)
    container = _get_container(job)
    status = DockerContainerEnum(container.status)
    return HTTPStatus.OK, JobStatusSchema(status=status)


@router.get("/jobs/{job_id}/logs", response={HTTPStatus.OK: JobLogsSchema})
def get_logs(request, job_id: str):
    job = Job.objects.get(id=job_id)

    container = _get_container(job)

    raw_logs = str(container.logs())
    if len(raw_logs) < 3:
        logs = []
    else:
        logs = raw_logs[2:-1].split("\\n")

    return HTTPStatus.OK, JobLogsSchema(logs=logs)


def _run_docker(job_id: UUID, docker_image_name: str, docker_environment: list):
    logger.info(f"Starting to pull {docker_image_name}..")
    container = docker_client.containers.run(
        docker_image_name,
        environment=docker_environment,
        stdout=True,
        stderr=True,
        detach=True,
        labels={"myoboku": settings.INSTANCE_NAME},
    )
    logger.info(f"Image {docker_image_name} pulled and run detached")
    job = Job.objects.get(id=job_id)
    job.container_id = container.id
    job.save()


def _get_container(job: Job):
    if not job.container_id:
        raise BadRequestException(detail=["This job is not bound to a container"])

    try:
        return docker_client.containers.get(job.container_id)
    except NotFound:
        raise BadRequestException(detail=["This job is not bound to a live container"])


def _is_overwhelmed():
    return len(_list_running_containers()) > settings.MAXIMUM_RUNNING_CONTAINER


def _list_running_containers() -> list[Model]:
    return docker_client.containers.list(
        filters={"status": "running", "label": f"myoboku={settings.INSTANCE_NAME}"}
    )
