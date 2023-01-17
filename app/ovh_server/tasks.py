from datetime import datetime
from time import sleep

from config.enums import JobStatusEnum
from ovh_server.models import OVHJob
from config.celery import app
from config.sdk import init_and_retrieve_client, send_log_file
from django.utils import timezone
from essential_generators import DocumentGenerator


@app.task(name="launch_job_task")
def launch_job(ovh_job_id):
    ovh_job = OVHJob.objects.get(id=ovh_job_id)
    print(ovh_job)
    client = init_and_retrieve_client(ovh_job)
    print(client)
    picsellia_job = client.get_job_by_id(ovh_job.env["job_id"])
    picsellia_job.send_logging("--#--part-0", "--#--part-0")
    sentence_generator = DocumentGenerator()
    task_length = get_task_length(ovh_job)
    logs = {}
    for i in range(1, task_length):
        log_section = f"--#--part-{i}"
        if i % 10 == 0:
            picsellia_job.send_logging(f"--#--part-{i}", f"--#--part-{i}")
            logs[log_section] = {
                "datetime": str(datetime.now().isoformat()),
                "logs": {},
            }
        else:
            log_string = sentence_generator.sentence()
            picsellia_job.send_logging(log_string, "--#--coucou")
            logs[log_section]["logs"][str(picsellia_job.line_nb)] = log_string
        sleep(1)

    picsellia_job.update_status(JobStatusEnum.SUCCESS)
    send_log_file(picsellia_job, logs)
    ovh_job.end_time = timezone.now()
    ovh_job.save()


def get_task_length(job: OVHJob) -> int:
    image_name = job.env["image"]
    if "small" in image_name:
        return 10
    elif "big" in image_name:
        return 100
    elif "mega" in image_name:
        return 1000
    else:
        return 20
