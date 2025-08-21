import argparse
import logging
import time
from dataclasses import dataclass
from json import JSONDecodeError

import docker
import docker.errors
import httpx
from httpx import TransportError

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, instance_name: str, docker_network: str | None):
        self.instance_name = instance_name
        self.docker_network = docker_network
        self.docker_client = docker.DockerClient(
            base_url="unix:///var/run/docker.sock", version="auto"
        )
        self.docker_client.ping()

    def start_job(self, job_id: str, docker_image_name: str, env: dict):
        print(f"pulling image {docker_image_name}")
        self.docker_client.images.pull(docker_image_name)
        docker_environment = [f"{key}={value}" for key, value in env.items()]
        self._run_container(job_id, docker_image_name, docker_environment)

    def _run_container(
        self, job_id: str, docker_image_name: str, docker_environment: list
    ):
        print(f"starting job {job_id} container with image {docker_image_name}")
        container = self.docker_client.containers.run(
            docker_image_name,
            environment=docker_environment,
            stdout=True,
            stderr=True,
            detach=True,
            labels={"myoboku": self.instance_name},
            network=self.docker_network,
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

    @staticmethod
    def _should_kill_job(job_id: str) -> bool:
        path = f"{settings.host}/api/v2/job/{job_id}/status"
        response = httpx.get(
            path,
            headers={"Authorization": f"Bearer {settings.token}"},
            timeout=30,
            follow_redirects=True,
        )
        if not response.is_success:
            print(f"status error {response.status_code} calling {path}")
            print(response.text)
            return False

        try:
            body = response.json()
            return body["status"].lower() == "killing"
        except JSONDecodeError:
            return False

    @staticmethod
    def _mark_job_killed(job_id: str) -> None:
        path = f"{settings.host}/api/v2/job/{job_id}/killed"
        response = httpx.post(
            path,
            headers={"Authorization": f"Bearer {settings.token}"},
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()


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
            print(content)
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
        _run()
    except KeyboardInterrupt:
        print("Shutting down..")
