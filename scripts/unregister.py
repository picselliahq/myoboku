import os
import sys

import orjson
import requests
from dotenv import load_dotenv

env_file_path = os.path.join(os.path.dirname(__file__), "..", "app", "config", ".env")
load_dotenv(env_file_path)
print(f"Reading .env file at: {env_file_path}")


def call_picsellia(url, payload, headers):
    response = requests.post(url=url, data=orjson.dumps(payload), headers=headers)
    response.raise_for_status()
    return response


if __name__ == "__main__":
    host = os.getenv("PICSELLIA_URL")
    if not host:
        print("Missing PICSELLIA_URL from env")
        sys.exit(1)
    organization_id = os.getenv("ORGANIZATION_ID")
    if not organization_id:
        print("Missing ORGANIZATION_ID from env")
        sys.exit(1)
    user_api_token = os.getenv("AUTHENTICATION_TOKEN")
    if not user_api_token:
        print("Missing AUTHENTICATION_TOKEN from env")
        sys.exit(1)
    url = f"{host}/sdk/organization/{organization_id}/myoboku"
    payload = {}
    headers = {"Authorization": f"Bearer {user_api_token}"}
    _ = call_picsellia(url, payload, headers)
    print("This training server is no longer registered as default server.")
