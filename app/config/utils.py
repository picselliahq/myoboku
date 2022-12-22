from urllib.parse import quote


def build_redis_url(
    host: str = "localhost",
    port: str | int = 6379,
    db: str | int | None = None,
    username: str | None = None,
    password: str | None = None,
) -> str:
    if password and not username:
        raise ValueError("Cannot build url with password but no username")
    url = "redis://"
    if username:
        url += quote(username, safe="")
        if password:
            url += f":{quote(password, safe='')}"
        url += "@"
    url += f"{host}:{port}"
    if db:
        db = db.lstrip("/")
        url += f"/{db}"
    return url
