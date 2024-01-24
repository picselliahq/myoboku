import enum
from typing import Optional
from uuid import UUID

from ninja import Schema


class JobInput(Schema):
    docker_image_name: str
    nb_cpu: int
    nb_gpu: int
    env: dict[str, str]
    docker_connector_id: Optional[UUID] = None


class JobSchema(Schema):
    id: UUID
    docker_image_name: str


class JobLogsSchema(Schema):
    logs: list[str]


class DockerContainerEnum(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    RESTARTING = "restarting"
    REMOVING = "removing"
    PAUSED = "paused"
    DEAD = "dead"

    EXITED = "exited"
    SUCCESS = "success"
    FAILED = "failed"


class JobStatusSchema(Schema):
    status: DockerContainerEnum
