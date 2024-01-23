import re
import secrets
import sys
from urllib.parse import urlparse

import orjson
import requests

pattern_uuid = r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"


def register_connector(organization_id, user_api_token, instance_name, instance_url):
    url = f"{host}/sdk/organization/{organization_id}/myoboku/register"
    payload = {"name": instance_name, "url": instance_url}
    headers = {"Authorization": f"Bearer {user_api_token}"}
    response = call_picsellia(url, payload, headers)
    return response.json()["token"]


def call_picsellia(url, payload, headers):
    response = requests.post(url=url, data=orjson.dumps(payload), headers=headers)
    response.raise_for_status()
    return response


def update_default_connector(organization_id, user_api_token, instance_name):
    url = f"{host}/sdk/organization/{organization_id}/myoboku"
    payload = {"name": instance_name}
    headers = {"Authorization": f"Bearer {user_api_token}"}
    _ = call_picsellia(url, payload, headers)


if __name__ == "__main__":
    print("Let's set up Myoboku")
    host = input("picsellia host [https://app.picsellia.com]:")
    if not host:
        host = "https://app.picsellia.com"

    host = host.removesuffix("/")
    host_domain = host.split("/")[-1]
    organization_id = input("organization id:")
    if not re.match(pattern_uuid, organization_id):
        print("This is not an uuid")
        sys.exit(1)

    user_api_token = input("user api token:")

    if not user_api_token:
        print("User api token can't be empty")
        sys.exit(1)

    instance_name = input("name of this instance:")
    if not instance_name:
        print("Instance name can't be empty")
        sys.exit(1)

    instance_url = input("url of this instance:")
    if not instance_url:
        print("Instance url can't be empty")
        sys.exit(1)

    instance_host = instance_url.removesuffix("/")
    instance_domain = urlparse(instance_host).hostname
    authentication_token = register_connector(
        organization_id, user_api_token, instance_name, instance_url
    )
    secret_key = secrets.token_hex(30)
    update_default_connector(organization_id, user_api_token, instance_name)

    with open("./app/config/.env", "w+") as f:
        f.write(f"AUTHENTICATION_TOKEN={authentication_token}\n")
        f.write(f"ORGANIZATION_ID={organization_id}\n")
        f.write("DEBUG=False\n")
        f.write("LOGGERS_DEBUG=\n")
        f.write("DJANGO_LOGLEVEL=INFO\n")
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"INSTANCE_NAME={instance_name}\n")
        f.write(f"PICSELLIA_URL={host}\n")
        f.write(f"ALLOWED_HOSTS={instance_domain}\n")

    print(f"Myoboku {instance_name} set up!")

    print("Run `python scripts/run.py`")
