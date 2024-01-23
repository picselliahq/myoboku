import subprocess

if __name__ == "__main__":
    try:
        subprocess.run(["python", "app/manage.py", "migrate"])
        subprocess.run(["python", "app/manage.py", "runserver", "8005"])
    except KeyboardInterrupt:
        print("Shutting down this server..")
