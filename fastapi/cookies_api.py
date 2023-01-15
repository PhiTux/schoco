import asyncio
import datetime
from io import BytesIO
import json
import queue
from typing import List
from pathlib import Path
import os
import shutil
from urllib.parse import urlencode
import docker
from math import ceil
import uuid
from multiprocessing import Queue, Manager
from threading import Lock, Thread
from config import settings
import pycurl

HOME = "/home/schoco"

COMPILETIME = 10


class ThreadSaveList():
    """List implementation, that stores a maximum number of items."""

    def __init__(self):
        self._list = list()
        self._lock = Lock()

    def append(self, value):
        with self._lock:
            self._list.append(value)
            return True

    def get(self, index):
        with self._lock:
            return self._list[index]

    def remove(self, index):
        with self._lock:
            self._list.pop(index)

    def length(self):
        with self._lock:
            return len(self._list)


newContainers = Queue(maxsize=settings.MAX_CONTAINERS)
"""Holds the infos of the new (running) cookies-containers, that are WAITING for usage."""

runningContainers = ThreadSaveList()


def writeFiles(files: List[str], uuid: str):
    dir = os.path.join(HOME, str(uuid))

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


def save_compilation_result(container_uuid: str, project_uuid: str):
    sourcepath = os.path.join(HOME, str(container_uuid))
    sourcefiles = os.listdir(sourcepath)
    destinationpath = os.path.join(HOME, str(project_uuid))
    Path(destinationpath).mkdir(exist_ok=True, parents=True)

    for file in sourcefiles:
        if file.endswith('.class'):
            shutil.move(os.path.join(sourcepath, file),
                        os.path.join(destinationpath, file))


def createNewContainer():
    """Creates (and runs!) new container and returns the id, uuid, ip and port."""
    new_uuid = uuid.uuid4()
    new_name = f"cookies-{new_uuid}"

    # create directory for this uuid
    uuid_dir = Path(os.path.join(HOME, str(new_uuid)))
    uuid_dir.mkdir(exist_ok=True, parents=True)

    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name="nproc", soft=1024, hard=1536)
    new_container = client.containers.run(
        'phitux/cookies', detach=True, auto_remove=True, remove=True, mem_limit="512m", name=new_name, network="schoco", ports={8080: ('127.0.0.1', None)}, stdout=True, stderr=True, stop_signal="SIGKILL", ulimits=[nproc_limit], user=os.getuid(), volumes=[f"{HOME}/{new_uuid}:/app/tmp"])
    # TODO place all schoco+cookies-containers in same schoco-network -> then a cookies-container can get called by its containername!!
    # -> user-defined bridge

    print("new container created")

    apiclient = docker.APIClient(base_url="unix://var/run/docker.sock")
    ip = apiclient.inspect_container(new_container.name)[
        'NetworkSettings']['Networks']['schoco']['IPAddress']
    port = apiclient.inspect_container(new_container.name)[
        'NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']

    return {'id': new_container.id, 'uuid': str(new_uuid), 'ip': ip, 'port': port}


def refillNewContainersQueue():
    """Just fills up the Queue to the amount of containers needed.
    Creates Containers. Runs every time when a command gets started and a container
    is removed from the Queue."""
    while not newContainers.qsize() + runningContainers.length() >= settings.MAX_CONTAINERS:
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


def prepareCompile(files: List[str]):
    # get next container out of queue
    # only get container, if running containers is < MAX_CONTAINERS

    # grab and prepare new container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for compilation within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)

    # write files to filesystem
    writeFiles(files, c['uuid'])

    # create websocket-attach-URL??

    return c


def startCompile(ip: str, port: int):

    # pycurl to cookies-java-server "/compile"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"http://localhost:{port}/compile")
    post_data = {'timeout_cpu': COMPILETIME, 'timeout_session': COMPILETIME}
    c.setopt(c.POSTFIELDS, json.dumps(post_data))
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    return json.loads(buffer.getvalue().decode('utf-8'))


def kill_n_create(container_uuid: str):
    """Kills the containers that was just executing a command and refills the queue of new (waiting) containers."""

    # remove containerInfo from runningContainers
    for i in range(runningContainers.length()):
        c = runningContainers.get(i)
        if c['uuid'] == container_uuid:
            runningContainers.remove(i)
            break

    # remove container-dir
    dir = os.path.join(HOME, container_uuid)
    print(dir)
    shutil.rmtree(dir)

    # kill and (hopefully automatically) remove container
    client = docker.from_env()
    try:
        c = client.containers.get(f"cookies-{container_uuid}")
    except (docker.errors.NotFound, docker.errors.APIError) as e:
        return

    if c.status == 'running':
        c.kill()
    else:
        c.remove(force=True)

    # refill newContainers
    refillNewContainersQueue()

# TODO Disable Networking on Container after start execution
# or use following command to enable Security Manager -> disable Networking, file access, ...:
# java -Djava.security.manager=default my.main.Class
