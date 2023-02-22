import pycurl
import os
from fastapi import HTTPException
from urllib.parse import urlencode
from config import settings
import json
import base64

try:
    from io import BytesIO
except:
    raise HTTPException(
        status_code=500, detail="Internel error with BytesIO")


def api_base_url():
    if settings.GITEA_HOST != "":
        full_host = settings.GITEA_HOST
        while full_host.endswith('/'):
            full_host = full_host[:-1]
    else:
        full_host = f"http://localhost:{settings.GITEA_LOCALHOST_PORT}"

    return f"{full_host}/api/v1"


def api_full_url(path: str):
    return f"{api_base_url()}{path}"


def create_repo(project_uuid: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url("/user/repos"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = {'name': project_uuid, 'private': True}
    c.setopt(c.POSTFIELDS, urlencode(post_data))
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False


def remove_repo(project_uuid: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, 'DELETE')
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False


def add_file(project_uuid: str, file_name: str, file_content: bytes):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents/{file_name}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    post_data = {'content': base64.b64encode(file_content)}
    c.setopt(c.POSTFIELDS, urlencode(post_data))
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False


def load_all_meta_content(project_uuid: str, path: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents{path}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        raise HTTPException(
            status_code=500, detail="Could not load contents from repo!")

    res = json.loads(buffer.getvalue().decode('utf-8'))

    content = []
    for i in range(len(res)):
        if res[i]['type'] == 'dir':
            content.append({'path': res[i]['path'], 'isDir': True})
        else:
            content.append({'path': res[i]['path'], 'isDir': False,
                            'download_url': res[i]['download_url'], 'sha': res[i]['sha']})

    return content


def download_file_by_url(url: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        raise HTTPException(
            status_code=500, detail="Could not load contents from repo!")

    return buffer.getvalue().decode('utf-8')


def update_file(project_uuid: str, path: str, content: str, sha: str):
    c = pycurl.Curl()
    c.setopt(c.VERBOSE, True)
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents/{path}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = {'content': base64.b64encode(
        content.encode('utf-8')), 'sha': sha}

    c.setopt(c.POSTFIELDS, urlencode(post_data))
    c.setopt(c.CUSTOMREQUEST, 'PUT')
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        return {}

    res = buffer.getvalue().decode('utf8')
    res = json.loads(res)

    return {'sha': res['content']['sha']}


def forkProject(orig_project_uuid: str, template_project_uuid: str):

    c = pycurl.Curl()
    c.setopt(c.VERBOSE, True)
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{orig_project_uuid}/forks"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = json.dumps({'name': template_project_uuid})
    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(pycurl.HTTPHEADER, [
             'Accept: application/json', 'Content-Type: application/json'])
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        return False

    return True
