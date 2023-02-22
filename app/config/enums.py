from django.db import models


class JobStatusEnum(models.TextChoices):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FINALIZING = "FINALIZING"
    INITIALIZING = "INITIALIZING"
    INTERRUPTED = "INTERRUPTED"
    INTERRUPTING = "INTERRUPTING"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    FAILED = "FAILED"