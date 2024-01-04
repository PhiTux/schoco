from io import BytesIO
import json
import queue
import time
import traceback
import models_and_schemas
from typing import List
from pathlib import Path
import os
import shutil
import docker
import uuid
from multiprocessing import Manager
from config import settings
import pycurl
from fastapi.logger import logger
import logging

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)

containers = "containers"
projects = "projects"

if settings.PRODUCTION:
    data_path = "/app/data"
else:
    data_path = settings.FULL_DATA_PATH


class ContainerList():
    #   """List implementation, that stores cookies-container-information."""

    def __init__(self):
        self._list = Manager().list()

    def append(self, value):
        self._list.append(value)
        return True

    def get(self, index):
        """Return item without removal."""
        return self._list[index]

    def remove(self, index):
        return self._list.pop(index)

    def remove_first(self, timeout):
        if len(self._list) > 0:
            return self._list.pop(0)
        else:
            return None

    def remove_by_uuid(self, container_uuid):
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                self._list.pop(i)
                break

    def get_and_remove_by_uuid(self, container_uuid):
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                return self._list.pop(i)

    def length(self):
        return len(self._list)

    def contains_uuid(self, container_uuid):
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                return True
        return False


m = Manager()
newContainers = m.Queue()  # maxsize=settings.MAX_CONTAINERS)
# """Holds the infos of the new (running) cookies-containers, that are WAITING for usage."""

runningContainers = ContainerList()
# containers that are doing something right now (compile, run, test)


def writeFiles(filesList: models_and_schemas.filesList, uuid: str):
    dir = os.path.join(data_path, str(uuid))

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
    for f in filesList.files:
        output_file = Path(os.path.join(dir, f.path))
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(f.content)


def recursivelyCopyClassFiles(sourcepath: str, destinationpath: str):
    sourcefiles = os.listdir(sourcepath)
    Path(destinationpath).mkdir(exist_ok=True, parents=True)

    filesExist = False
    sourcefiles = os.listdir(sourcepath)
    for file in sourcefiles:
        if file.endswith('.class'):
            filesExist = True
            shutil.copyfile(os.path.join(sourcepath, file),
                            os.path.join(destinationpath, file))
        elif os.path.isdir(os.path.join(sourcepath, file)):
            if recursivelyCopyClassFiles(os.path.join(
                    sourcepath, file), os.path.join(destinationpath, file)):
                filesExist = True
    return filesExist


def save_compilation_result(container_uuid: str, project_uuid: str):
    sourcepath = os.path.join(data_path, containers, str(container_uuid))
    destinationpath = os.path.join(
        data_path, projects, str(project_uuid))

    recursivelyCopyClassFiles(sourcepath, destinationpath)


def remove_compilation_result(project_uuid: str):
    destinationpath = os.path.join(data_path, projects, str(project_uuid))
    if os.path.exists(destinationpath):
        shutil.rmtree(destinationpath)


def remove_container_content(container_uuid: str):
    dir = os.path.join(data_path, containers, str(container_uuid))
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
                return False
        return True
    return False


def createNewContainer():
    """Creates (and runs!) new container and returns the id, uuid and port."""
    new_uuid = uuid.uuid4()
    new_name = f"schoco-cookies-{new_uuid}"

    # build and create directory for this uuid
    uuid_dir = Path(os.path.join(
        settings.FULL_DATA_PATH, containers, str(new_uuid)))
    """This variable is a parameter for the container and thus must always be an OS-path"""

    create_dir = Path(os.path.join(data_path, containers, str(new_uuid)))
    create_dir.mkdir(exist_ok=True, parents=True)

    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name="nproc", soft=3700, hard=5000)
    new_container = client.containers.run(
        "phitux/schoco-cookies:1.2.0", detach=True, auto_remove=True, remove=True, mem_limit="512m", name=new_name, network="schoco", ports={'8080/tcp': ('127.0.0.1', None)}, stdin_open=True, stdout=True, stderr=True, stop_signal="SIGKILL", tty=True, ulimits=[nproc_limit], user=f"{os.getuid()}:{os.getgid()}", volumes=[f"{uuid_dir}:/app/tmp"])

    apiclient = docker.APIClient(base_url="unix://var/run/docker.sock")
    # ip = apiclient.inspect_container(new_name)[
    #    'NetworkSettings']['Networks']['schoco']['IPAddress']
    port = apiclient.inspect_container(new_name)[
        'NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']

    # 'ip': ip,
    return {'id': new_container.id, 'uuid': str(new_uuid), 'port': port, 'in_use': False}


def refillNewContainersQueue():
    """Just fills up the Queue to the amount of containers needed.
    Runs every time when a command ends and a container
    is removed from runningContainers."""
    while (runningContainers.length() + newContainers.qsize()) < settings.MAX_CONTAINERS:
        newContainers.put(createNewContainer())


def fillNewContainersQueue():
    """runs ONCE at start of schoco (called in main.py)"""
    if newContainers.qsize() > 0:
        return

    # remove older cookies-containers if any
    client = docker.from_env()
    containers = client.containers.list(all=True)
    for c in containers:
        if str(c.name).startswith('schoco-cookies-'):
            # kill container
            try:
                if c.status == 'running':
                    c.kill()
                    # gets autoremoved since auto-removing is set to true
                else:
                    c.remove(force=True)
            except:
                print("concurrent deletion of same container")

    refillNewContainersQueue()


def prepareCompile(filesList: models_and_schemas.filesList):
    # get next container out of queue - return if no new one is available after 3 seconds.
    # prepare the container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return None

    runningContainers.append(c)

    # write files to filesystem
    writeFiles(filesList, os.path.join(containers, c['uuid']))

    return c


def startCompile(uuid: str, port: int, computation_time: int, save_output: bool):

    # pycurl to cookies-java-server "/compile"
    buffer = BytesIO()
    c = pycurl.Curl()
    if settings.PRODUCTION:
        host = f"schoco-cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/compile")
    post_data = {'timeout_cpu': computation_time,
                 'timeout_session': computation_time,
                 'save_output': save_output}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            break
        except:
            print("connection error: " + str(port))
            tries -= 1
            if (tries == 0):
                c.close()
                return {'status': 'connect_error'}
            time.sleep(0.2)
    c.close()

    return json.loads(buffer.getvalue().decode('utf-8'), strict=False)


def remove_all_container_dirs():
    """Removes all container-dirs (and thus all files)"""
    dir = os.path.join(data_path, containers)
    if os.path.exists(dir):
        shutil.rmtree(dir)


def kill_all_containers():
    """Kills all containers that are still running."""
    client = docker.from_env()
    containers = client.containers.list(all=True)
    for c in containers:
        if str(c.name).startswith('schoco-cookies-'):
            try:
                if c.status == 'running':
                    c.kill()
                else:
                    c.remove(force=True)
            except:
                print("concurrent deletion of same container")


def kill_container(container_uuid: str):
    # kill and (hopefully automatically) remove container
    client = docker.from_env()
    try:
        c = client.containers.get(f"schoco-cookies-{container_uuid}")
    except docker.errors.NotFound as e:
        print("container not found")
        return False
    except docker.errors.APIError as e:
        print(e)
        print(traceback.format_exc())
        return False

    if c.status == 'running':
        c.kill()
    else:
        c.remove(force=True)

    # remove containerInfo from runningContainers
    runningContainers.remove_by_uuid(container_uuid)

    # remove container-dir
    dir = os.path.join(data_path, containers, container_uuid)
    shutil.rmtree(dir)

    return True


def kill_n_create(container_uuid: str):
    """Kills the container that was just executing a command and refills the queue of new (waiting) containers."""
    kill_container(container_uuid)

    # refill newContainers
    refillNewContainersQueue()


def put_container_back_in_new_queue(c: dict):
    """Puts a container from runningContainers back in the newContainers queue."""
    c = runningContainers.get_and_remove_by_uuid(c['uuid'])
    newContainers.put(c)


def prepare_execute(project_uuid: str, user_id: int):
    # grab and prepare new container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for compilation within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)

    # copy .class files to container-mount
    sourcepath = os.path.join(data_path, projects,
                              f"{project_uuid}_{user_id}")
    if not os.path.exists(sourcepath):
        put_container_back_in_new_queue(c)
        return {'executable': False}

    destinationpath = os.path.join(
        data_path, containers, str(c['uuid']))
    Path(destinationpath).mkdir(exist_ok=True, parents=True)

    filesExist = recursivelyCopyClassFiles(sourcepath, destinationpath)

    # if no .class files existed, then return container to newContainers-Queue
    if not filesExist:
        put_container_back_in_new_queue(c)
        return {'executable': False}

    return c


def start_execute(uuid: str, port: int, computation_time: int, save_output: bool, entry_point: str):

    # pycurl to cookies-java-server "/execute"
    buffer = BytesIO()
    c = pycurl.Curl()
    if settings.PRODUCTION:
        host = f"schoco-cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/execute")

    post_data = {'timeout_cpu': computation_time,
                 'timeout_session': computation_time,
                 'save_output': save_output,
                 'entry_point': entry_point}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.CONNECTTIMEOUT_MS, 50)
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


def start_test(uuid: str, port: int, computation_time: int):

    # pycurl to cookies-java-server "/test"
    buffer = BytesIO()
    c = pycurl.Curl()

    if settings.PRODUCTION:
        host = f"schoco-cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/test")

    post_data = {'timeout_cpu': computation_time,
                 'timeout_session': computation_time}

    # Why the 7? 🤷‍♂️ Probability and trial and error...
    tries = 7
    while tries > 0:
        try:
            c.setopt(c.POSTFIELDS, json.dumps(post_data))
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.CONNECTTIMEOUT_MS, 50)
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

    # hack to check, if JUnit-testing ran into a security error. It's a bit ugly but should work...
    # Otherwise the text is no valid json since the quote gets closed too early.
    if ("at java.lang.SecurityManager" in buffer.getvalue().decode('utf-8')):
        return {'status': 'security_error'}

    results = json.loads(buffer.getvalue().decode('utf-8'), strict=False)

    # parse results
    lines = results['stdout'].strip().splitlines()
    lastLine = lines[-1]
    if lastLine.startswith('OK'):
        passed_tests = int(lastLine.split('(')[1].split(')')[0].split()[0])
        results['passed_tests'] = passed_tests
        results['failed_tests'] = 0
    elif lastLine.startswith('Tests run'):
        failed_tests = int(lastLine.split(',')[1].split(':')[1].strip())
        passed_tests = int(lastLine.split(',')[0].split(':')[
            1].strip()) - failed_tests
        results['passed_tests'] = passed_tests
        results['failed_tests'] = failed_tests
    else:
        results['passed_tests'] = 0
        results['failed_tests'] = 0

    return results
