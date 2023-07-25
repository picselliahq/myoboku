from uuid import uuid4

from django.db import models
from django.utils import timezone


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    killed_at = models.DateTimeField(default=None, null=True, blank=True)

    docker_image_name = models.CharField(max_length=512)
    docker_environment = models.JSONField(default=dict)
    nb_cpu = models.PositiveIntegerField(default=8)
    nb_gpu = models.PositiveIntegerField(default=0)

    docker_connector_id = models.UUIDField(null=True, blank=True)

    container_id = models.CharField(max_length=128)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Job {self.id} has image {self.docker_image_name}. container id:{self.container_id}"
