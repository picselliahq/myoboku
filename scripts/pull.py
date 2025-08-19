import argparse
import logging
import time
from threading import Thread

import httpx

from myoboku.external import docker_client

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, instance_name: str, docker_network: str | None):
        self.instance_name = instance_name
        self.docker_network = docker_network

    def start_job(self, docker_image_name: str, env: dict):
        docker_client.ping()

        print(f"Pulling with image {docker_image_name}")
        docker_environment = [f"{key}={value}" for key, value in env.items()]
        thread = Thread(
            target=self._run_docker,
            args=(docker_image_name, docker_environment),
        )
        thread.start()
        print(f"Launching image {docker_image_name}")

    def _run_docker(self, docker_image_name: str, docker_environment: list):
        print(f"Starting to pull {docker_image_name}..")
        container = docker_client.containers.run(
            docker_image_name,
            environment=docker_environment,
            stdout=True,
            stderr=True,
            detach=False,
            labels={"myoboku": self.instance_name},
            network=self.docker_network,
        )
        print(
            f"Image {docker_image_name} pulled and run detached on container {container}"
        )


def _run(
    picsellia_url: str,
    organization_id: str,
    token: str,
    instance_name: str,
    docker_network: str,
    sleeping_time: int,
):
    path = picsellia_url + f"/api/organization/{organization_id}/myoboku/jobs"
    while True:
        response = httpx.post(
            path,
            json={"name": instance_name},
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 204:
            print("Nothing to do... waiting")
        elif response.status_code == 200:
            content = response.json()
            JobService(instance_name, docker_network).start_job(
                content["docker_image_name"], content["env"]
            )
        else:
            print(f"Error, status code is {response.status_code}")
        time.sleep(sleeping_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="https://app.picsellia.com")
    parser.add_argument("--instance", type=str, required=True)
    parser.add_argument("--organization", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--docker-network", type=str, default=None)
    parser.add_argument("--sleep", type=int, default=10)
    args = parser.parse_args()
    try:
        _run(
            args.host,
            args.organization,
            args.token,
            args.instance,
            args.docker_network,
            args.sleep,
        )
    except KeyboardInterrupt:
        print("Shutting down..")
