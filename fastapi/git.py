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

    return full_host


def api_full_url(path: str):
    return f"{api_base_url()}/api/v1{path}"


def replace_base_url(url: str):
    return f"{api_base_url()}/{url.split('/', 3)[3]}"


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


def load_all_meta_content(project_uuid: str, id: int, path: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    if id == 0:
        c.setopt(c.URL, api_full_url(
            f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents{path}"))
    else:
        c.setopt(c.URL, api_full_url(
            f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents{path}?ref={id}"))
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


def download_Tests_java(project_uuid):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL,
             f"{api_base_url()}/{settings.GITEA_USERNAME}/{project_uuid}/raw/branch/main/Tests.java")
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        raise HTTPException(
            status_code=500, detail="Could not load contents from repo!")

    return buffer.getvalue().decode('utf-8')


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


def update_file(project_uuid: str, user_id: int, path: str, content: str, sha: str):
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/contents/{path}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = {'content': base64.b64encode(
                 content.encode('utf-8')).decode('utf-8'), 'sha': sha}
    if user_id != 0:
        post_data['branch'] = str(user_id)

    c.setopt(c.POSTFIELDS, json.dumps(post_data))
    c.setopt(pycurl.HTTPHEADER, [
             'Accept: application/json', 'Content-Type: application/json'])
    c.setopt(c.CUSTOMREQUEST, 'PUT')
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        print(buffer.getvalue().decode('utf8'))
        return {}

    res = buffer.getvalue().decode('utf8')
    res = json.loads(res)

    return {'sha': res['content']['sha']}


def get_recent_commit_by_project_uuid(project_uuid: str):
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{project_uuid}/commits"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    # c.setopt(pycurl.HTTPHEADER, [
    #         'Accept: application/json', 'Content-Type: application/json'])
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        return 0

    res = buffer.getvalue().decode('utf8')
    res = json.loads(res)

    return res[0]['sha']


def create_branch(uuid: str, new_branch: int):
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{uuid}/branches"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = json.dumps(
        {'new_branch_name': str(new_branch), 'old_branch_name': "main"})

    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(pycurl.HTTPHEADER, [
             'Accept: application/json', 'Content-Type: application/json'])
    # c.setopt(c.CUSTOMREQUEST, 'PUT')
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if not (res_code >= 200 and res_code < 300):
        print(buffer.getvalue().decode('utf8'))
        return False

    # res = buffer.getvalue().decode('utf8')
    # res = json.loads(res)

    return True


def remove_branch(uuid: str, branch: int):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{uuid}/branches/{branch}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CUSTOMREQUEST, 'DELETE')
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False


def renameFile(old_path: str, new_path: str, uuid: str, user_id: int, content: str, sha: str):
    # PUT /repos/{owner}/{repo}/contents/{filepath}
    # url-filepath ist neue Datei, in BODY: from_path, branch, content, sha

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(
        f"/repos/{settings.GITEA_USERNAME}/{uuid}/contents/{new_path}"))
    c.setopt(c.USERPWD, f"{settings.GITEA_USERNAME}:{settings.GITEA_PASSWORD}")
    post_data = {'content': base64.b64encode(
                 content.encode('utf-8')).decode('utf-8'), 'sha': sha}

    if user_id != 0:
        post_data['branch'] = str(user_id)

    post_data['from_path'] = old_path

    c.setopt(c.POSTFIELDS, json.dumps(post_data))
    c.setopt(pycurl.HTTPHEADER, [
        'Accept: application/json', 'Content-Type: application/json'])
    c.setopt(c.CUSTOMREQUEST, 'PUT')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False
