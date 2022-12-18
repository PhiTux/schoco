from fastapi import APIRouter, Depends
import auth
import database
import models_and_schemas
import crud
from sqlmodel import Session

code = APIRouter()


@code.post('/createNewHelloWorld', dependencies=[Depends(auth.oauth2_scheme)])
def createNewHelloWorld(projectName: models_and_schemas.ProjectName, db: Session = Depends(database.get_db), username=Depends(auth.get_username_by_token)):
    print(username)
    print(projectName)

    return ""
