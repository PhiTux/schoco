import pycurl
import os
from fastapi import HTTPException
from urllib.parse import urlencode
import json
import base64

try:
    from io import BytesIO
except:
    raise HTTPException(
        status_code=500, detail="Internel error with BytesIO")


def get_port():
    if 'GITEA_PORT' in os.environ:
        return os.environ.get('GITEA_PORT')
    return 3000


def get_username():
    if 'GITEA_USERNAME' in os.environ:
        return os.environ.get('GITEA_USERNAME')
    return 'schoco'


def get_password():
    if 'GITEA_PASSWORD' in os.environ:
        return os.environ.get('GITEA_PASSWORD')
    return 'schoco1234'


def api_base_url():
    return f"http://localhost:{get_port()}/api/v1"


def api_full_url(path: str):
    return f"{api_base_url()}{path}"


def create_repo(project_uuid: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url("/user/repos"))
    c.setopt(c.USERPWD, f"{get_username()}:{get_password()}")
    post_data = {'name': project_uuid, 'private': True}
    c.setopt(c.POSTFIELDS, urlencode(post_data))
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False

    res = json.loads(buffer.getvalue().decode('utf-8'))
    print(res['id'])


def remove_repo(project_uuid: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, api_full_url(f"/repos/{get_username()}/{project_uuid}"))
    c.setopt(c.USERPWD, f"{get_username()}:{get_password()}")
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
        f"/repos/{get_username()}/{project_uuid}/contents/{file_name}"))
    c.setopt(c.USERPWD, f"{get_username()}:{get_password()}")
    c.setopt(c.WRITEDATA, buffer)
    post_data = {'content': base64.b64encode(file_content)}
    c.setopt(c.POSTFIELDS, urlencode(post_data))
    c.perform()
    res_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if (res_code >= 200 and res_code < 300):
        return True
    return False
