from django.db import models


class JobRunStatus(models.TextChoices):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    KILLED = "KILLED"


class JobType(models.TextChoices):
    PROCESS_DATASET_VERSION = "PROCESS_DATASET_VERSION"
    LAUNCH_TRAINING = "LAUNCH_TRAINING"
    CONTINUOUS_TRAINING = "CONTINUOUS_TRAINING"
