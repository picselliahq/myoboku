import docker

docker_client = docker.DockerClient(
    base_url="unix:///var/run/docker.sock", version="auto"
)
