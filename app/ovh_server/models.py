from django.db import models
from uuid import UUID
from uuid import uuid4
from django.utils import timezone

from config.enums import JobStatusEnum


class OVHJob(models.Model):
    id: UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=None, null=True, blank=True)
    image: str = models.CharField(default="", max_length=256)
    env: dict = models.JSONField(default=dict)
    nb_cpu: int = models.PositiveIntegerField(default=8)
    nb_gpu: int = models.PositiveIntegerField(default=0)
    status: JobStatusEnum = models.CharField(
        max_length=16, choices=JobStatusEnum.choices, default=JobStatusEnum.PENDING
    )
    task_id: UUID = models.UUIDField(default=uuid4)

    class Meta:
        ordering = ("-start_time",)
