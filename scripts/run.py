import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        subprocess.run(["python", "app/manage.py", "migrate"])
        subprocess.run(["python", "app/manage.py", "runserver", str(args.port)])
    except KeyboardInterrupt:
        print("Shutting down this server..")
