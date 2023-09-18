import enum
from typing import Optional
from uuid import UUID

from ninja import Schema


class JobInput(Schema):
    docker_image_name: str
    nb_cpu: int
    nb_gpu: int
    env: dict[str, str]
    docker_connector_id: Optional[UUID]


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
    EXITED = "exited"
    DEAD = "dead"


class JobStatusSchema(Schema):
    status: DockerContainerEnum
