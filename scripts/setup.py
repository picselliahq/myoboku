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


PULL = True

if __name__ == "__main__":
    print("Let's set up Myoboku")
    print(
        "PULL=True, so it will be configured in PULL mode ! Myoboku as a server is not available at the moment"
    )

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

    if not PULL:
        instance_url = input("url of this instance:")
        if not instance_url:
            print("Instance url can't be empty")
            sys.exit(1)
        instance_host = instance_url.removesuffix("/")
        instance_domain = urlparse(instance_host).hostname
    else:
        # this won't be used by the platform
        instance_url = f"https://{instance_name}.invalid"
        instance_domain = f"{instance_name}.invalid"

    authentication_token = register_connector(
        organization_id, user_api_token, instance_name, instance_url
    )
    secret_key = secrets.token_hex(30)
    update_default_connector(organization_id, user_api_token, instance_name)

    print(f"Myoboku {instance_name} set up!")

    if PULL:
        print(
            f'Run poetry run python scripts/pull.py --host="{host}" --instance="{instance_name}" --organization="{organization_id}" --sleep=10 --token="{user_api_token}"'
        )
    else:
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
        print("Run `poetry run python scripts/run.py`")
