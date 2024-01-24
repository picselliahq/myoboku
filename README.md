# myoboku
Picsellia Job launcher

## Prerequisites

* Python 3.10+
* [Poetry](https://python-poetry.org/) to install the dependencies

## Setup and run

```shell
poetry install
poetry run scripts/setup.py
poetry run scripts/run.py
```

## Run myoboku with systemd

To run the server in the background, you'll need to copy the `myoboku.service` file to `/etc/systemd/system` and edit it.

You'll need to change:
* The user that will run the process (`User=` line)
* The path to the poetry executable (`ExecStart=` line)
* The path to the myoboku folder (`WorkingDirectory=` line)

Then, run the following commands as root:
```shell
systemctl daemon-reload           # Load the new myoboku.service file
systemctl start myoboku.service   # Start the service
systemctl enable myoboku.service  # Enable the service at boot
```
