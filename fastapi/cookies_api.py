from io import BytesIO
import json
import queue
import time
import traceback
from typing import List
from pathlib import Path
import os
import shutil
import docker
import uuid
from multiprocessing import Manager
from threading import Lock
from config import settings
import pycurl


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
        """Return item without removal."""
        with self._lock:
            return self._list[index]

    def remove(self, index):
        with self._lock:
            self._list.pop(index)

    def remove_by_uuid(self, container_uuid):
        with self._lock:
            for i in range(len(self._list)):
                if self._list[i]['uuid'] == container_uuid:
                    self._list.pop(i)
                    break

    def get_and_remove_by_uuid(self, container_uuid):
        with self._lock:
            for i in range(len(self._list)):
                if self._list[i]['uuid'] == container_uuid:
                    c = self._list.pop(i)
                    return c

    def length(self):
        with self._lock:
            return len(self._list)


m = Manager()
newContainers = m.Queue(maxsize=settings.MAX_CONTAINERS)
"""Holds the infos of the new (running) cookies-containers, that are WAITING for usage."""

runningContainers = ThreadSaveList()


def writeFiles(files: List[str], uuid: str):
    dir = os.path.join(settings.FULL_DATA_PATH, str(uuid))

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
    sourcepath = os.path.join(settings.FULL_DATA_PATH, str(container_uuid))
    sourcefiles = os.listdir(sourcepath)
    destinationpath = os.path.join(settings.FULL_DATA_PATH, str(project_uuid))
    Path(destinationpath).mkdir(exist_ok=True, parents=True)

    print(sourcepath)
    print(sourcefiles)
    for file in sourcefiles:
        if file.endswith('.class'):
            print("-> " + file)
            shutil.move(os.path.join(sourcepath, file),
                        os.path.join(destinationpath, file))


def createNewContainer():
    """Creates (and runs!) new container and returns the id, uuid, ip and port."""
    new_uuid = uuid.uuid4()
    new_name = f"cookies-{new_uuid}"

    # create directory for this uuid
    uuid_dir = Path(os.path.join(settings.FULL_DATA_PATH, str(new_uuid)))
    uuid_dir.mkdir(exist_ok=True, parents=True)

    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name="nproc", soft=1024, hard=1536)
    new_container = client.containers.run(
        'phitux/cookies', detach=True, auto_remove=True, remove=True, mem_limit="512m", name=new_name, network="schoco", ports={'8080/tcp': ('127.0.0.1', None)}, stdin_open=True, stdout=True, stderr=True, stop_signal="SIGKILL", tty=True, ulimits=[nproc_limit], user=os.getuid(), volumes=[f"{uuid_dir}:/app/tmp"])
    # TODO place all schoco+cookies-containers in same schoco-network -> then a cookies-container can get called by its containername!!
    # -> user-defined bridge

    print("new container created: " + str(new_uuid))

    apiclient = docker.APIClient(base_url="unix://var/run/docker.sock")
    ip = apiclient.inspect_container(new_name)[
        'NetworkSettings']['Networks']['schoco']['IPAddress']
    port = apiclient.inspect_container(new_name)[
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
            # remove dir

            dir = os.path.join(settings.FULL_DATA_PATH, c.name[8:])
            if os.path.exists(dir):
                shutil.rmtree(dir)

            # kill container
            if c.status == 'running':
                c.kill()
                # gets autoremoved since auto-removing is set to true
            else:
                c.remove(force=True)

    refillNewContainersQueue()


def prepareCompile(files: List[str]):
    # get next container out of queue - return if no new one is available after 3 seconds.
    # prepare the container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for compilation within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)
    print("prepared: " + c['uuid'] + " with port: " + str(c['port']))

    # write files to filesystem
    writeFiles(files, c['uuid'])

    return c


def startCompile(ip: str, port: int):
    print("start compile at port: " + str(port))

    # pycurl to cookies-java-server "/compile"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"http://localhost:{port}/compile")
    post_data = {'timeout_cpu': COMPILETIME, 'timeout_session': COMPILETIME}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            break
        except BaseException as e:
            print("connection error: " + str(port))
            tries -= 1
            if (tries == 0):
                c.close()
                return {'status': 'connect_error'}
            time.sleep(0.2)
    c.close()

    return json.loads(buffer.getvalue().decode('utf-8'), strict=False)


def kill_n_create(container_uuid: str):
    """Kills the containers that was just executing a command and refills the queue of new (waiting) containers."""

    print("kill " + container_uuid)

    # remove containerInfo from runningContainers
    runningContainers.remove_by_uuid(container_uuid)

    # remove container-dir
    dir = os.path.join(settings.FULL_DATA_PATH, container_uuid)
    shutil.rmtree(dir)

    # kill and (hopefully automatically) remove container
    client = docker.from_env()
    try:
        c = client.containers.get(f"cookies-{container_uuid}")
    except (docker.errors.NotFound, docker.errors.APIError) as e:
        print(e)
        print(traceback.format_exc())
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


def prepare_execute(project_uuid: str):
    # grab and prepare new container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for execution within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)

    # copy .class files to container-mount
    sourcepath = os.path.join(settings.FULL_DATA_PATH, project_uuid)
    sourcefiles = os.listdir(sourcepath)
    destinationpath = os.path.join(settings.FULL_DATA_PATH, str(c['uuid']))
    Path(destinationpath).mkdir(exist_ok=True, parents=True)

    filesExist = False
    for file in sourcefiles:
        if file.endswith('.class'):
            filesExist = True
            shutil.copyfile(os.path.join(sourcepath, file),
                            os.path.join(destinationpath, file))

    # if no .class files existed, then return container to newContainers-Queue
    if not filesExist:
        c = runningContainers.get_and_remove_by_uuid(c['uuid'])
        newContainers.put(c)

        return {'executable': False}

    print(c['uuid'] + " with port " + c['port'])

    return c


def start_execute(ip: str, port: int):
    print("start execute at port: " + str(port))

    # pycurl to cookies-java-server "/execute"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"http://localhost:{port}/execute")
    post_data = {'timeout_cpu': COMPILETIME, 'timeout_session': COMPILETIME}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            break
        except BaseException as e:
            print("connection error: " + str(port))
            tries -= 1
            if (tries == 0):
                c.close()
                return {'status': 'connect_error'}
            time.sleep(0.2)
    c.close()

    print(buffer.getvalue().decode('utf-8'))

    return json.loads(buffer.getvalue().decode('utf-8'), strict=False)


def start_test(ip: str, port: int):
    print("start test at port: " + str(port))

    # pycurl to cookies-java-server "/test"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"http://localhost:{port}/test")
    post_data = {'timeout_cpu': COMPILETIME, 'timeout_session': COMPILETIME}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            break
        except BaseException as e:
            print("connection error: " + str(port))
            tries -= 1
            if (tries == 0):
                c.close()
                return {'status': 'connect_error'}
            time.sleep(0.2)
    c.close()

    print(buffer.getvalue().decode('utf-8'))

    return json.loads(buffer.getvalue().decode('utf-8'), strict=False)
