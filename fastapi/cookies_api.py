import datetime
from typing import List
from pathlib import Path
import os
import shutil
import docker
from math import ceil
import uuid
from multiprocessing import Queue

HOME = "/home/schoco"


def get_max_containers():
    """Amount of running (=executing) containers. Defaults to 8."""

    if 'MAX_CONTAINERS' in os.environ:
        return os.environ.get('MAX_CONTAINERS')
    return 8


newContainers = Queue(maxsize=ceil(get_max_containers()/3))
"""Holds the infos of the new (running) cookies-containers, that are WAITING for usage. Defaults to MAX_CONTAINERS/3"""

runningContainers = Queue(maxsize=get_max_containers())


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


def createNewContainer():
    """Creates (and runs!) new container and returns the id, uuid, and open Port."""
    new_uuid = uuid.uuid4()
    new_name = f"cookies-{new_uuid}"

    # create directory for this uuid
    uuid_dir = Path(os.path.join(HOME, new_uuid))
    uuid_dir.parent.mkdir(exist_ok=True, parents=True)

    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name="nproc", soft=1024, hard=1536)
    new_container = client.containers.run(
        'phitux/cookies', detach=True, auto_remove=True, remove=True, mem_limit="512m", name=new_name, network="schoco", ports={8080: ('127.0.0.1', 80)}, stdout=True, stderr=True, stop_signal="SIGKILL", ulimits=[nproc_limit], user=os.getuid(), volumes=[f"{HOME}/{new_uuid}:/app/tmp"])
    # TODO place all schoco+cookies-containers in same schoco-network -> then a cookies-container can get called by its containername!!
    # -> user-defined bridge

    apiclient = docker.APIClient(base_url="unix://var/run/docker.sock")
    print(apiclient.inspect_container(new_container.name)[
          'NetworkSettings']['Networks']['bridge']['IPAddress'])


def refillNewContainersQueue():
    """Just fills up the Queue to the amount of containers needed. 
    Creates Containers. Runs every time when a command gets started and a container
    is removed from the Queue."""
    while not newContainers.full():
        newContainers.put(createNewContainer())


def fillNewContainersQueue():
    """runs ONCE at start of schoco (called in main.py)"""
    # remove older cookies-containers if any
    client = docker.from_env()
    containers = client.containers.list(all=True)
    for c in containers:
        if str(c.name).startswith('cookies-'):
            if c.status == 'running':
                c.kill()
                # gets autoremoved since auto-removing is set to true
            else:
                c.remove(force=True)

    refillNewContainersQueue()


def prepareCompile(files: List[str], project_uuid: str):
    # get next container out of queue and refill queue
    # only get container, if running containers is < MAX_CONTAINERS

    c = newContainers.get()
    refillNewContainersQueue()

    # write files to filesystem
    writeFiles(files, project_uuid)

    return

    # create container via Docker API
    client = docker.from_env()
    container = client.containers.get("cookies")
    log = container.exec_run(
        "sh -c 'bash /app/cookies.sh \"javac /app/tmp/Main.java\" 10 10; exit'", stdin=True, stderr=True, stdout=True)
    print(log)

    # return URLs


# TODO Disable Networking on Container after start execution
# or use following command to enable Security Manager -> disable Networking, file access, ...:
# java -Djava.security.manager=default my.main.Class
