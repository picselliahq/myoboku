# Generated by Django 4.2.3 on 2023-08-07 14:00

import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "killed_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                ("docker_image_name", models.CharField(max_length=512)),
                ("docker_environment", models.JSONField(default=dict)),
                ("nb_cpu", models.PositiveIntegerField(default=8)),
                ("nb_gpu", models.PositiveIntegerField(default=0)),
                ("docker_connector_id", models.UUIDField(blank=True, null=True)),
                ("container_id", models.CharField(max_length=128)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
