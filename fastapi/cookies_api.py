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

COMPILETIME = 10

if settings.PRODUCTION:
    data_path = "/app/data"
else:
    data_path = settings.FULL_DATA_PATH


class ContainerList():
    #   """List implementation, that stores cookies-container-information."""

    def __init__(self):
        self._list = Manager().list()
#        self._lock = Lock()

    def append(self, value):
        #        with self._lock:
        self._list.append(value)
        return True

    def get(self, index):
        """Return item without removal."""
#        with self._lock:
        return self._list[index]

    def remove(self, index):
        #        with self._lock:
        return self._list.pop(index)

    def remove_first(self, timeout):
        #        with self._lock:

        if len(self._list) > 0:
            return self._list.pop(0)
        else:
            return None

    def remove_by_uuid(self, container_uuid):
        #        with self._lock:
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                self._list.pop(i)
                break

    def get_and_remove_by_uuid(self, container_uuid):
        #        with self._lock:
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                return self._list.pop(i)

    def length(self):
        #        with self._lock:
        return len(self._list)

    def contains_uuid(self, container_uuid):
        #        with self._lock:
        for i in range(len(self._list)):
            if self._list[i]['uuid'] == container_uuid:
                return True
        return False


m = Manager()
newContainers = m.Queue()  # maxsize=settings.MAX_CONTAINERS)
# newContainers = ThreadSaveList()
# """Holds the infos of the new (running) cookies-containers, that are WAITING for usage."""

runningContainers = ContainerList()


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


def save_compilation_result(container_uuid: str, project_uuid: str):
    sourcepath = os.path.join(data_path, str(container_uuid))
    sourcefiles = os.listdir(sourcepath)
    destinationpath = os.path.join(data_path, str(project_uuid))
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

    # build and create directory for this uuid
    uuid_dir = Path(os.path.join(settings.FULL_DATA_PATH, str(new_uuid)))
    """This variable is a parameter for the container and thus must always be an OS-path"""

    create_dir = Path(os.path.join(data_path, str(new_uuid)))
    create_dir.mkdir(exist_ok=True, parents=True)

    client = docker.from_env()
    nproc_limit = docker.types.Ulimit(name="nproc", soft=3700, hard=5000)
    new_container = client.containers.run(
        'phitux/cookies', detach=True, auto_remove=True, remove=True, mem_limit="512m", name=new_name, network="schoco", ports={'8080/tcp': ('127.0.0.1', None)}, stdin_open=True, stdout=True, stderr=True, stop_signal="SIGKILL", tty=True, ulimits=[nproc_limit], user=f"{os.getuid()}:{os.getgid()}", volumes=[f"{uuid_dir}:/app/tmp"])
    # TODO place all schoco+cookies-containers in same schoco-network -> then a cookies-container can get called by its containername!!
    # -> user-defined bridge

    apiclient = docker.APIClient(base_url="unix://var/run/docker.sock")
    ip = apiclient.inspect_container(new_name)[
        'NetworkSettings']['Networks']['schoco']['IPAddress']
    port = apiclient.inspect_container(new_name)[
        'NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']

    return {'id': new_container.id, 'uuid': str(new_uuid), 'ip': ip, 'port': port, 'in_use': False}


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
        if str(c.name).startswith('cookies-'):
            print("remove container name:", str(c.name))
            print("remove container id:", str(c.id))

            # remove dir
            try:
                dir = os.path.join(data_path, c.name[8:])
                if os.path.exists(dir):
                    shutil.rmtree(dir)
            except:
                print("couldn't remove directory:", dir)

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
    # get next container out of queue - return if no new one is available after 2 seconds.
    # prepare the container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for compilation within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)
    print("prepared: " + c['uuid'] + " with port: " + str(c['port']))

    # write files to filesystem
    writeFiles(filesList, c['uuid'])

    return c


def startCompile(uuid: str, ip: str, port: int):
    print("start compile at port: " + str(port))

    # pycurl to cookies-java-server "/compile"
    buffer = BytesIO()
    c = pycurl.Curl()
    if settings.PRODUCTION:
        host = f"cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/compile")
    post_data = {'timeout_cpu': COMPILETIME, 'timeout_session': COMPILETIME}

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


def kill_n_create(container_uuid: str):
    """Kills the containers that was just executing a command and refills the queue of new (waiting) containers."""

    print("kill " + container_uuid)

    # remove containerInfo from runningContainers
    runningContainers.remove_by_uuid(container_uuid)

    # remove container-dir
    dir = os.path.join(data_path, container_uuid)
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


def prepare_execute(project_uuid: str, user_id: int):
    # grab and prepare new container and place it inside runningContainers
    try:
        c = newContainers.get(timeout=3)
    except queue.Empty:
        return {'success': False, 'message': 'No worker ready for compilation within 3 seconds 😥 Please retry!'}

    runningContainers.append(c)

    # copy .class files to container-mount
    sourcepath = os.path.join(data_path, f"{project_uuid}_{user_id}")
    sourcefiles = os.listdir(sourcepath)
    destinationpath = os.path.join(data_path, str(c['uuid']))
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
        newContainers.append(c)

        return {'executable': False}

    return c


def start_execute(uuid: str, ip: str, port: int):
    print("start execute at port: " + str(port))

    # pycurl to cookies-java-server "/execute"
    buffer = BytesIO()
    c = pycurl.Curl()
    if settings.PRODUCTION:
        host = f"cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/execute")

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


def start_test(uuid: str, ip: str, port: int):
    print("start test at port: " + str(port))

    # pycurl to cookies-java-server "/test"
    buffer = BytesIO()
    c = pycurl.Curl()

    if settings.PRODUCTION:
        host = f"cookies-{uuid}:8080"
    else:
        host = f"localhost:{port}"
    c.setopt(c.URL, f"http://{host}/test")

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

    # TODO: Save results in DB

    return results
