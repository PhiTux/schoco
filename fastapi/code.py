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
    print(username)
    print(projectName)

    project_uuid = uuid.uuid4()
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

    return project_uuid

    # create project-representation in DB
    if not crud.create_project(db=db, project=project):
        # delete git repo
        git.remove_repo(project_uuid=project_uuid)

        raise HTTPException(
            status_code=500, detail="Could not create project")

    return project
