from fastapi import APIRouter, Depends, HTTPException
import auth
import database
import models_and_schemas
import crud
import uuid
import os
import git
from sqlmodel import Session

code = APIRouter()


@code.post('/createNewHelloWorld', dependencies=[Depends(auth.oauth2_scheme)])
def createNewHelloWorld(projectName: models_and_schemas.ProjectName, db: Session = Depends(database.get_db), username=Depends(auth.get_username_by_token)):

    project_uuid = str(uuid.uuid4())
    user = crud.get_user_by_username(db=db, username=username)
    project = models_and_schemas.Project(
        name=projectName.projectName, uuid=project_uuid, owner_id=user.id)

    # create git repo
    if not git.create_repo(project_uuid):
        raise HTTPException(status_code=500, detail="Could not create project")

    # load the template files into the git repo
    for file in os.listdir("./java_helloWorld"):
        file_content = open(file=f"./java_helloWorld/{file}", mode="rb").read()
        if not git.add_file(project_uuid=project_uuid,
                            file_name=file, file_content=file_content):
            git.remove_repo(project_uuid=project_uuid)
            raise HTTPException(
                status_code=500, detail="Could not create project")

    # create project-representation in DB
    if not crud.create_project(db=db, project=project):
        # delete git repo
        git.remove_repo(project_uuid=project_uuid)

        raise HTTPException(
            status_code=500, detail="Could not create project")

    return project_uuid


def project_access_allowed(project_uuid: str, username: str, db: Session):
    # teacher is allowed to open
    user = crud.get_user_by_username(db=db, username=username)
    if user.role == "teacher":
        return True

    # otherwise: user must be owner
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project.owner.username == username:
        return True
    return False


results = []


def recursively_download_all_files(project_uuid: str, path: str):
    global results

    root = git.load_all_meta_content(
        project_uuid=project_uuid, path=path)

    # download all files
    for c in root:
        if not c['isDir']:
            results.append({c['path']:  git.download_file_by_url(
                url=c['download_url'])})
        else:
            recursively_download_all_files(
                project_uuid=project_uuid, path=f"/{c['path']}/")

    return (results)


@code.post('/loadAllFiles', dependencies=[Depends(auth.oauth2_scheme)])
def loadAllFiles(project_uuid: models_and_schemas.ProjectUuid, db: Session = Depends(database.get_db), username=Depends(auth.get_username_by_token)):
    project_uuid = project_uuid.project_uuid
    global results
    results = []

    # check if user may open this project
    if not project_access_allowed(project_uuid=project_uuid, username=username, db=db):
        raise HTTPException(
            status_code=405, detail="You're not allowed to open this project")

    res = recursively_download_all_files(project_uuid=project_uuid, path="/")

    return res
