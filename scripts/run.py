import os
import subprocess


def find_instance_url():
    path = "app/config/.env"
    if not os.path.exists(path):
        raise RuntimeError(
            "This app has not been setup configured properly, please run `setup.py` before running `run.py`: .env file not found in app/config."
        )

    with open("app/config/.env") as f:
        for line in f.readlines():
            if line.startswith("INSTANCE_URL"):
                return (
                    line.split("=")[1].rstrip("\n").lstrip("http://").lstrip("https://")
                )
    raise RuntimeError(
        "This app has not been setup configured properly, please run `setup.py` before running `run.py`: INSTANCE_URL not found in .env"
    )


if __name__ == "__main__":
    instance_url = find_instance_url()
    try:
        subprocess.run(["python", "app/manage.py", "migrate"])
        subprocess.run(["python", "app/manage.py", "runserver", instance_url])
    except KeyboardInterrupt:
        print("Shutting down this server..")
