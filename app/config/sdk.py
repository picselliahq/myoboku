from picsellia import Client, Job, Experiment
from datetime import datetime
import json


def init_and_retrieve_client(job) -> Client:
    client = Client(
        api_token=job.env["api_token"],
        organization_id=job.env["organization_id"],
        host="http://127.0.0.1:8000",
    )
    return client


def send_log_file(picsellia_job: Job, logs: dict):
    logs_path = "{}-logs.json".format(picsellia_job.id)
    with open(logs_path, "w") as f:
        logs["exit_code"] = {
            "exit_code": "0",
            "datetime": str(datetime.now().isoformat()),
        }
        json.dump(logs, f)
    picsellia_job.store_logging_file(logs_path)


def store_experiment_logs(experiment: Experiment, logs: dict):
    logs_path = "{}-logs.json".format(experiment.id)
    with open(logs_path, "w") as f:
        logs["exit_code"] = {
            "exit_code": "0",
            "datetime": str(datetime.now().isoformat()),
        }
        json.dump(logs, f)
    experiment.store_logging_file(logs_path)
