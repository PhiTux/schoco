import datetime
from typing import List
from pathlib import Path
import os
import shutil
import docker

HOME = "/home/schoco"


def writeFiles(files: List[str], project_uuid: str):
    dir = os.path.join(HOME, project_uuid)

    # check if dir is already existing -> delete content
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    # write files
    for f in files:
        output_file = Path(os.path.join(dir, f.path))
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(f.content)


def createCompile(files: List[str], project_uuid: str):
    # write files to filesystem
    writeFiles(files, project_uuid)

    # create container via Docker API
    client = docker.from_env()
    container = client.containers.get("cookies")
    log = container.exec_run(
        "sh -c 'bash /app/cookies.sh \"javac /app/tmp/Main.java\" 10 10; exit'", stdin=True, stderr=True, stdout=True)
    print(log)

    # return URLs
