import argparse
import json
import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime

import docker
import docker.errors
import httpx
import picsellia
from docker.models.containers import Container
from docker.types import DeviceRequest
from docker.utils import parse_repository_tag
from httpx import TransportError
from rich.progress import Progress

logger = logging.getLogger(__name__)


def has_gpu():
    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


class JobService:
    def __init__(self, instance_name: str, docker_network: str | None):
        self.instance_name = instance_name
        self.docker_network = docker_network
        self.docker_client = docker.DockerClient(
            base_url="unix:///var/run/docker.sock", version="auto"
        )
        self.docker_client.ping()
        self.has_gpu = has_gpu()

    def start_job(self, job_id: str, docker_image_name: str, env: dict):
        print(f"Pulling image: {docker_image_name}")
        repository, image_tag = parse_repository_tag(docker_image_name)
        tag = image_tag or "latest"
        try:
            self._pull_image(repository, tag)
            docker_environment = [f"{key}={value}" for key, value in env.items()]
            self._run_container(job_id, docker_image_name, docker_environment)
        except docker.errors.ImageNotFound as e:
            print(str(e))
            self._mark_job_failed(job_id)

    def _pull_image(self, repository: str, tag: str) -> None:
        with Progress() as progress:
            tasks = {}
            resp = self.docker_client.api.pull(
                repository, tag=tag, stream=True, decode=True
            )

            for line in resp:
                try:
                    self._show_progress(tasks, line, progress)
                except KeyError as e:
                    print(str(e))

    @staticmethod
    def _show_progress(tasks: dict, line: dict, progress: Progress):
        if line["status"] == "Downloading":
            id = f"[red][Download {line['id']}]"
        elif line["status"] == "Extracting":
            id = f"[green][Extract  {line['id']}]"
        else:
            return

        if id not in tasks.keys():
            try:
                tasks[id] = progress.add_task(
                    f"{id}", total=line["progressDetail"]["total"]
                )
            except KeyError:
                pass
        else:
            progress.update(tasks[id], completed=line["progressDetail"]["current"])

    def _run_container(
        self, job_id: str, docker_image_name: str, docker_environment: list
    ):
        print(f"starting job {job_id} container with image {docker_image_name}")
        device_request = (
            [DeviceRequest(count=-1, capabilities=[["gpu"]])] if self.has_gpu else None
        )
        container = self.docker_client.containers.run(
            docker_image_name,
            environment=docker_environment,
            stdout=True,
            stderr=True,
            detach=True,
            labels={"myoboku": self.instance_name},
            network=self.docker_network,
            device_requests=device_request,
            shm_size="5G",
        )
        print(f"started container {container} run with image {docker_image_name}")

        while True:
            time.sleep(10)
            if self._should_kill_job(job_id):
                print(f"killing job {job_id} container {container}")
                container.stop()
                print(f"killed job {job_id} container {container}")
                self._mark_job_killed(job_id)
                print(f"mark job {job_id} as killed")
                break

            try:
                container.reload()
            except docker.errors.NotFound:
                print(f"job {job_id} container {container} not found")
                break

            if container.status in ("exited", "dead", "removing"):
                print(f"job {job_id} container {container} stopped")
                break

        if container.status != "removing":
            container.reload()
            exit_code = container.attrs["State"]["ExitCode"]
            if exit_code == 1:
                print(f"job {job_id} finished with status code 1")
                now = str(datetime.now(tz=UTC).isoformat())
                formatted_logs = {
                    "--#--Initialize_run": {
                        "logs": {
                            str(line_nb): line.decode("utf-8")
                            for line_nb, line in enumerate(container.logs(stream=True))
                        },
                        "datetime": now,
                    },
                    "exit_code": {
                        "exit_code": str(container.attrs["State"]["ExitCode"]),
                        "datetime": now,
                    },
                }
                print(formatted_logs)
            elif exit_code != 0:
                print(f"uploading logs for job {job_id}")
                self._save_container_logs(job_id, container)
                self._mark_job_failed(job_id)

        try:
            container.remove()
        except docker.errors.NotFound:
            pass
        print(f"job {job_id} finished")

    def _should_kill_job(self, job_id: str) -> bool:
        status = self._get_job_status(job_id)
        return status == "killing"

    @staticmethod
    def _get_job_status(job_id: str) -> str:
        path = f"/api/v2/job/{job_id}/status"
        response = client.connexion.get(path)
        body = response.json()
        return body["status"].lower()

    @staticmethod
    def _mark_job_killed(job_id: str) -> None:
        response = client.connexion.post(f"/api/v2/job/{job_id}/killed")
        response.raise_for_status()

    @staticmethod
    def _mark_job_failed(job_id: str) -> None:
        response = client.connexion.post(f"/api/v2/job/{job_id}/fail")
        response.raise_for_status()

    @staticmethod
    def _save_container_logs(job_id: str, container: Container) -> None:
        with tempfile.NamedTemporaryFile("w+") as logs_file:
            now = str(datetime.now(tz=UTC).isoformat())
            formatted_logs = {
                "--#--Initialize_run": {
                    "logs": {
                        str(line_nb): line.decode("utf-8")
                        for line_nb, line in enumerate(container.logs(stream=True))
                    },
                    "datetime": now,
                },
                "exit_code": {
                    "exit_code": str(container.attrs["State"]["ExitCode"]),
                    "datetime": now,
                },
            }

            json.dump(formatted_logs, logs_file)
            logs_file.flush()

            job = client.get_job_by_id(job_id)
            job.store_logging_file(logs_file.name)


def _run():
    path = f"{settings.host}/api/organization/{settings.organization}/myoboku/jobs"
    service = JobService(settings.instance, settings.docker_network)
    while True:
        try:
            response = httpx.post(
                path,
                json={"name": settings.instance},
                headers={"Authorization": f"Bearer {settings.token}"},
                timeout=30,
            )
        except TransportError as exc:
            print(f"Transport Error: {exc!r}")
            time.sleep(settings.sleep)
            continue

        if response.status_code == 204:
            print("Nothing to do... waiting")
        elif response.status_code == 200:
            content = response.json()
            service.start_job(
                content["job_id"],
                content["docker_image_name"],
                content["env"],
            )
        else:
            print(f"Error, status code is {response.status_code}")
        time.sleep(settings.sleep)


@dataclass
class Settings:
    host: str
    instance: str
    organization: str
    token: str
    docker_network: str | None
    sleep: int


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="https://app.picsellia.com")
    parser.add_argument("--instance", type=str, required=True)
    parser.add_argument("--organization", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--docker-network", type=str, default=None)
    parser.add_argument("--sleep", type=int, default=10)
    args = parser.parse_args()
    settings = Settings(**args.__dict__)
    try:
        client = picsellia.Client(
            host=settings.host,
            api_token=settings.token,
            organization_id=settings.organization,
        )
        _run()
    except KeyboardInterrupt:
        print("Shutting down..")
