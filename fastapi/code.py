from io import BytesIO
import json
import zipfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, UploadFile
from fastapi.responses import StreamingResponse
import auth
import database_config
import models_and_schemas
import crud
import cookies_api
import uuid
import os
import git
from sqlmodel import Session

code = APIRouter(prefix="/api")

DEFAULT_COMPUTATION_TIME = 10


@code.post('/createNewHelloWorld', dependencies=[Depends(auth.oauth2_scheme)])
def createNewHelloWorld(newProject: models_and_schemas.newProject, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    if newProject.projectName.strip() == "":
        raise HTTPException(status_code=400, detail="Project name empty")

    project_uuid = str(uuid.uuid4())
    user = crud.get_user_by_username(db=db, username=username)
    project = models_and_schemas.Project(
        name=newProject.projectName, description=newProject.projectDescription, uuid=project_uuid, owner_id=user.id, computation_time=DEFAULT_COMPUTATION_TIME)

    # create git repo
    if not git.create_repo(project_uuid):
        raise HTTPException(status_code=500, detail="Could not create project")

    # load the template files into the git repo
    # don't load Tests.java if user is a pupil
    for file in os.listdir("./java_helloWorld"):
        if file.endswith(".class") or (user.role == "pupil" and file == "Tests.java"):
            continue
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


def project_access_allowed(project_uuid: str, user_id: str, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    # teacher is allowed to open
    user = crud.get_user_by_username(db=db, username=username)
    if user.role == "teacher":
        return True

    if int(user_id) == 0:
        # otherwise: user must be owner of project...
        project = crud.get_project_by_project_uuid(
            db=db, project_uuid=project_uuid)
        if project != None and project.owner.username == username:
            return True

    else:
        # ...or he is trying to open his branch (of a homework)
        if int(user_id) == user.id:
            return True

    raise HTTPException(
        status_code=405, detail="You're not allowed to open or edit this project")


def project_access_allowed_teacher_only(project_uuid: str, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    # user must be teacher
    user = crud.get_user_by_username(db=db, username=username)
    if user.role != "teacher":
        raise HTTPException(
            status_code=405, detail="You're not allowed to open or edit this project")

    # user must be owner
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    print(project_uuid)
    if project.owner.username == username:
        return True

    raise HTTPException(
        status_code=405, detail="You're not allowed to open or edit this project")


results = []


def recursively_download_all_files(project_uuid: str, id: int, path: str):
    global results

    root = git.load_all_meta_content(
        project_uuid=project_uuid, id=id, path=path)

    # download all files
    for c in root:
        if not c['isDir']:
            # skip Tests.java if it's a pupil's-branch
            if id != 0 and c['path'] == 'Tests.java':
                continue
            results.append({'path': c['path'], 'content': git.download_file_by_url(
                url=git.replace_base_url(c['download_url'])), 'sha': c['sha']})
        else:
            recursively_download_all_files(
                project_uuid=project_uuid, path=f"/{c['path']}/")

    return (results)


@ code.get('/loadAllFiles/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def loadAllFiles(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    global results
    results = []

    res = recursively_download_all_files(
        project_uuid=project_uuid, id=user_id, path="/")

    return res


@ code.post('/updateDescription/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def saveDescription(updateDescription: models_and_schemas.updateText, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    result = crud.update_description(
        db=db, project_uuid=project_uuid, description=updateDescription.text)
    return result


@code.post('/updateProjectName/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def saveProjectName(updateProjectName: models_and_schemas.updateText, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if updateProjectName.text.strip() == "":
        raise HTTPException(
            status_code=400, detail="Project name must be at least 3 characters long")

    result = crud.update_project_name(
        db=db, project_uuid=project_uuid, name=updateProjectName.text)
    return result


@ code.get('/getProjectInfo/{project_uuid}/{user_id}', dependencies=[Depends(auth.oauth2_scheme)])
def getProjectName(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)

    homework = crud.get_homework_by_template_uuid(db=db, uuid=project_uuid)
    isHomework = True
    if homework == None:
        isHomework = False

    result = {"name": project.name,
              "description": project.description, "isHomework": isHomework}

    if isHomework and user_id != 0:
        user = crud.get_user_by_id(db=db, id=user_id)
        result['fullusername'] = user.full_name
        result['deadline'] = homework.deadline

    return result


@ code.post('/saveFileChanges/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def saveFileChanges(fileChanges: models_and_schemas.FileChangesList, project_uuid: str = Path(), user_id: int = Path()):

    success = []
    for f in fileChanges.changes:
        res = git.update_file(project_uuid, user_id, f.path, f.content, f.sha)
        if res:
            success.append(
                {'path': f.path, 'content': f.content, 'sha': res['sha']})

    return success


@code.get('/getProjectsAsTeacher', dependencies=[Depends(auth.check_teacher)])
def getProjectsAsTeacher(db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    all_homework = crud.get_teachers_homework_by_username(
        db=db, username=username)

    # own projects:
    all_projects = crud.get_projects_by_username(db=db, username=username)

    homework = []
    projects = []

    for p in all_projects:
        # if project is part of a homework then save it in homeworks...
        is_homework = False
        for h in all_homework:
            if p.id == h.template_project_id:
                is_homework = True
                course = crud.get_course_by_id(db=db, id=h.course_id)
                homework.append({"deadline": h.deadline, "name": p.name, "description": p.description, "id": h.id,
                                "course_name": course.name, "course_color": course.color, "course_font_dark": course.fontDark})
                # TODO append "edited by X/Y pupils" and "average points of solutions"
                break

        # ...otherwise its a regular project
        if not is_homework:
            projects.append(
                {"name": p.name, "description": p.description, "uuid": p.uuid})

    return {"homework": homework, "projects": projects}


@code.get('/getProjectsAsPupil')
def getProjectsAsPupil(db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)

    all_projects = crud.get_projects_by_username(db=db, username=username)

    all_editing_homework = crud.get_editing_homework_by_username(
        db=db, username=username)

    all_new_homework = crud.get_pupils_homework_by_username(
        db=db, username=username)

    homework = []

    for h in all_new_homework:
        already_edited = False
        for e in all_editing_homework:
            if h["id"] == e.homework_id:
                # append those homeworks, that are already edited
                already_edited = True
                uuid = crud.get_uuid_of_homework(
                    db=db, homework_id=h['id'])
                homework.append({"is_editing": True, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                                "id": h["id"], "uuid": uuid, "branch": user.id})
                break
        # ... and those, which are not yet started by the pupil
        if not already_edited:
            homework.append({"is_editing": False, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                             "id": h["id"]})

    return {"homework": homework, "projects": all_projects}


def getComputationTime(db: Session, project_uuid: str):
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    return project.computation_time


@ code.post('/prepareCompile/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def prepareCompile(filesList: models_and_schemas.filesList, project_uuid: str = Path(), user_id: int = Path()):

    # separately load Tests.java from homework-template if I'm watching a pupil's solution (user_id != 0)
    if user_id != 0:
        tests = git.download_Tests_java(project_uuid=project_uuid)
        filesList.files.append(models_and_schemas.File(
            path="Tests.java", content=tests))

    # write files to container-mount and return WS-URL
    c = cookies_api.prepareCompile(filesList)

    return c


@ code.post('/startCompile/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def startCompile(startCompile: models_and_schemas.startCompile, background_tasks: BackgroundTasks, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):

    computation_time = getComputationTime(db=db, project_uuid=project_uuid)

    result = cookies_api.startCompile(
        startCompile.container_uuid, startCompile.port, computation_time)

    if user_id != 0:
        crud.increase_compiles(db=db, uuid=project_uuid, user_id=user_id)

    # save compilation-results (.class-files)
    cookies_api.save_compilation_result(
        startCompile.container_uuid, f"{project_uuid}_{user_id}")

    # before return: start background_task to refill new_containers
    background_tasks.add_task(
        cookies_api.kill_n_create, startCompile.container_uuid)

    return result


@ code.get('/prepareExecute/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def prepareExecute(project_uuid: str = Path(), user_id: int = Path()):

    # prepares container by copying .class files into container-mount
    # returns {'executable': false} if no files are found
    c = cookies_api.prepare_execute(project_uuid, user_id)
    return c


@ code.post('/startExecute/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def startExecute(startExecute: models_and_schemas.startExecute, background_tasks: BackgroundTasks, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):

    computation_time = getComputationTime(db=db, project_uuid=project_uuid)

    result = cookies_api.start_execute(
        startExecute.container_uuid, startExecute.port, computation_time)

    if user_id != 0:
        crud.increase_runs(db=db, uuid=project_uuid, user_id=user_id)

    background_tasks.add_task(
        cookies_api.kill_n_create, startExecute.container_uuid)

    return result


@ code.get('/prepareTest/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def prepareTest(project_uuid: str = Path(), user_id: int = Path()):
    # we now use "prepare_execute", since it is (at least until now) the same code
    c = cookies_api.prepare_execute(project_uuid, user_id)
    return c


@ code.post('/startTest/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def startTest(startTest: models_and_schemas.startTest, background_tasks: BackgroundTasks, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):

    computation_time = getComputationTime(db=db, project_uuid=project_uuid)

    result = cookies_api.start_test(
        startTest.container_uuid, startTest.port, computation_time)

    if user_id != 0 and not ("status" in result and result["status"] == "security_error"):
        crud.increase_tests(db=db, uuid=project_uuid, user_id=user_id)
        crud.save_test_result(db=db, uuid=project_uuid,
                              user_id=user_id, result=result)

    background_tasks.add_task(
        cookies_api.kill_n_create, startTest.container_uuid)

    return result


@ code.post('/createHomework/{project_uuid}', dependencies=[Depends(project_access_allowed_teacher_only)])
def createHomework(create_homework: models_and_schemas.create_homework, project_uuid: str = Path(), db: Session = Depends(database_config.get_db)):

    orig_project_uuid = project_uuid
    template_project_uuid = str(uuid.uuid4())

    # create new repo
    if not git.create_repo(template_project_uuid):
        return False
    # add files
    for f in create_homework.files:
        if not git.add_file(template_project_uuid, f.path, str.encode(f.content)):
            git.remove_repo(template_project_uuid)
            return False

    # copy project-entry in database
    project = crud.get_project_by_project_uuid(db, orig_project_uuid)
    if project == None:
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    original_project_id = project.id

    new_project = models_and_schemas.Project(
        uuid=template_project_uuid, name=project.name, description=project.description, owner_id=project.owner_id, computation_time=create_homework.computation_time)
    if not crud.create_project(db=db, project=new_project):
        # delete git repo
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    # prepare to create Homework-entry
    p = crud.get_project_by_project_uuid(db, template_project_uuid)

    template_project_id = p.id

    homework = models_and_schemas.Homework(course_id=create_homework.course_id, template_project_id=template_project_id,
                                           original_project_id=original_project_id, deadline=create_homework.deadline_date)

    if not crud.create_homework(db,
                                homework=homework):
        git.remove_repo(project_uuid=template_project_uuid)
        crud.remove_project_by_uuid(db=db, project_uuid=new_project.uuid)
        return False

    return True


@code.post('/startHomework', dependencies=[Depends(auth.oauth2_scheme)])
def startHomework(homeworkId: models_and_schemas.homeworkId, username=Depends(auth.get_username_by_token), db: Session = Depends(database_config.get_db)):
    id = homeworkId.id

    user = crud.get_user_by_username(db=db, username=username)

    # get homework
    try:
        homework = crud.get_homework_by_id(db=db, id=id)
    except:
        raise HTTPException(
            status_code=500, detail=f"Could not find homework with id {id}.")

    # get project_uuid from project_id
    template_project = crud.get_project_by_id(
        db=db, id=homework.template_project_id)

    # create branch
    if not git.create_branch(uuid=template_project.uuid, new_branch=user.id):
        raise HTTPException(
            status_code=409, detail="You're already working on this Homework.")

    # create editing_homework - otherwise remove repo
    editing_homework = models_and_schemas.EditingHomework(
        homework_id=id, owner_id=user.id)
    if not crud.create_editing_homework(db,
                                        editing_homework=editing_homework):
        git.remove_branch(uuid=template_project.uuid, branch=user.id)
        raise HTTPException(
            status_code=500, detail=f"Error on starting homework with id {id}.")

    return {'success': True, 'uuid': template_project.uuid, 'branch': user.id}


@code.post('/getHomeworkInfo', dependencies=[Depends(auth.check_teacher)])
def getHomeworkInfo(homeworkId: models_and_schemas.homeworkId, db: Session = Depends(database_config.get_db)):
    id = homeworkId.id

    # get project_name and course_badge_info
    homework = crud.get_homework_by_id(db=db, id=id)
    template_project = crud.get_project_by_id(
        db=db, id=homework.template_project_id)

    result = {"name": template_project.name, "uuid": template_project.uuid, "course_name": homework.course.name,
              "course_color": homework.course.color, "course_font_dark": homework.course.fontDark}

    # get each user's results
    pupils = crud.get_all_users_of_course_id(db=db, id=homework.course_id)
    editing_homework = crud.get_all_editing_homework_by_homework_id(
        db=db, id=id)

    pupils_results = []
    for p in pupils:
        found = False
        for eh in editing_homework:
            if p.id == eh.owner_id:
                found = True
                pupils_results.append({"name": p.full_name, "username": p.username, "uuid": template_project.uuid, "branch": p.id, "result": eh.submission,
                                      "compilations": eh.number_of_compilations, "runs": eh.number_of_runs, "tests": eh.number_of_tests})
                break

        if not found:
            pupils_results.append({"name": p.full_name, "username": p.username, "uuid": "",
                                  "best_result": "", "compilations": 0, "runs": 0, "tests": 0})

    result['pupils_results'] = pupils_results

    return result


@code.post('/deleteHomework', dependencies=[Depends(auth.check_teacher)])
def deleteHomework(homework_id: models_and_schemas.homeworkId, db: Session = Depends(database_config.get_db)):
    homework = crud.get_homework_by_id(db=db, id=homework_id.id)
    if homework == None:
        return False

    template_project = crud.get_project_by_id(
        db=db, id=homework.template_project_id)
    if template_project == None:
        return False

    # delete git repo
    if not git.remove_repo(project_uuid=template_project.uuid):
        print("Error on deleting git repo: " + template_project.uuid)

    # delete db template_project
    if not crud.remove_project_by_uuid(db=db, project_uuid=template_project.uuid):
        print("Error on deleting project: " + template_project.uuid)

    # delete db editing_homework
    if not crud.remove_all_editing_homework_by_homework_id(
            db=db, id=homework_id.id):
        print("Error on deleting editing_homeworks of homework_id: " + homework_id.id)

    # delete db homework
    if not crud.remove_homework_by_id(db=db, id=homework_id.id):
        print("Error on deleting homework: " + homework_id.id)
        return False

    return True


@ code.post('/deleteProject/{project_uuid}', dependencies=[Depends(auth.oauth2_scheme)])
def deleteProject(user_id: models_and_schemas.UserById, project_uuid: str = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    # delete db project
    # if user_id is 0: check if user is owner
    if user_id.user_id == 0:
        project = crud.get_project_by_project_uuid(
            db=db, project_uuid=project_uuid)
        if project == None:
            return False

        user = crud.get_user_by_username(db=db, username=username)
        if user.id != project.owner_id:
            return False

        # remove project from db
        if not crud.remove_project_by_uuid(db=db, project_uuid=project_uuid):
            return False

        # delete git repo
        if not git.remove_repo(project_uuid=project_uuid):
            return False

    else:
        # remove editing_homework from db
        if not crud.remove_editing_homework_by_uuid_and_user_id(db=db, uuid=project_uuid, user_id=user_id.user_id):
            return False

        # delete git branch
        if not git.remove_branch(uuid=project_uuid, branch=user_id.user_id):
            return False

    return True


@code.post('/renameFile/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def renameFile(file: models_and_schemas.RenameFile, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if file.new_path.strip() == "":
        raise HTTPException(
            status_code=400, detail="Wrong input: New path is empty.")

    if not git.renameFile(file.old_path, file.new_path, project_uuid, user_id, file.content, file.sha):
        raise HTTPException(
            status_code=500, detail="Error on renaming file.")

    return {'success': True}


@code.post('/renameHomework', dependencies=[Depends(auth.check_teacher)])
def renameHomework(homework: models_and_schemas.RenameHomework, db: Session = Depends(database_config.get_db)):
    if homework.new_name.strip() == "":
        raise HTTPException(
            status_code=400, detail="Wrong input: New name is empty.")

    if not crud.rename_homework(db=db, id=homework.id, new_name=homework.new_name):
        raise HTTPException(
            status_code=500, detail="Error on renaming homework.")

    return {'success': True}


@code.post('/renameProject/{project_uuid}', dependencies=[Depends(auth.oauth2_scheme)])
def renameProject(new_name: models_and_schemas.updateText, project_uuid: str = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    # check if user is owner
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: Project not found.")
    user = crud.get_user_by_username(db=db, username=username)
    if user == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: User not found.")
    if user.id != project.owner_id:
        raise HTTPException(
            status_code=400, detail="Wrong input: User is not owner of project.")

    # check name input
    if new_name.text.strip() == "":
        raise HTTPException(
            status_code=400, detail="Wrong input: New name is empty.")

    if not crud.rename_project(db=db, uuid=project_uuid, new_name=new_name.text):
        raise HTTPException(
            status_code=500, detail="Error on renaming project.")

    return {'success': True}


@code.post('/duplicateProject/{project_uuid}', dependencies=[Depends(auth.oauth2_scheme)])
def duplicateProject(project_uuid: str = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)
    if user == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: User not found.")

    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: Project not found.")

    if project.owner_id != user.id:
        raise HTTPException(
            status_code=400, detail="Wrong input: User is not owner of project.")

    # download all files
    global results
    results = []

    res = recursively_download_all_files(
        project_uuid=project_uuid, id=0, path="/")

    new_project_uuid = str(uuid.uuid4())

    # create new repo
    if not git.create_repo(new_project_uuid):
        return False
    # add files
    for f in res:
        if not git.add_file(new_project_uuid, f['path'], str.encode(f['content'])):
            git.remove_repo(new_project_uuid)
            return False

    # create db project entry
    orig_project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)

    new_project = models_and_schemas.Project(uuid=new_project_uuid, name=orig_project.name + " (copy)",
                                             description=orig_project.description, owner_id=user.id, computation_time=orig_project.computation_time)

    if not crud.create_project(db=db, project=new_project):
        # delete git repo
        git.remove_repo(project_uuid=new_project_uuid)
        return False

    return {'success': True}


@code.get('/downloadProject/{uuid}', dependencies=[Depends(auth.oauth2_scheme)])
def downloadProject(uuid: str = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)
    if user == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: User not found.")

    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=uuid)
    if project == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: Project not found.")

    if project.owner_id != user.id:
        raise HTTPException(
            status_code=400, detail="Wrong input: User is not owner of project.")

    global results
    results = []

    # download all files
    res = recursively_download_all_files(
        project_uuid=uuid, id=0, path="/")

    # download project info
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=uuid)
    meta = {"name": project.name, "description": project.description}

    if user.role == "teacher":
        meta["computation_time"] = project.computation_time

    # create zip file
    zip_bytes_io = BytesIO()
    with zipfile.ZipFile(zip_bytes_io, 'w', zipfile.ZIP_DEFLATED) as zipped:
        for f in res:
            zipped.writestr(os.path.join("code", f['path']), f['content'])
        zipped.writestr("meta.json", json.dumps(meta, ensure_ascii=False))

    response = StreamingResponse(
        iter([zip_bytes_io.getvalue()]), media_type="application/x-zip-compressed", headers={"Content-Disposition": f"attachment;filename={project.name}.zip", "Content-Length": str(zip_bytes_io.getbuffer().nbytes)})

    return response


@code.post('/uploadProject', dependencies=[Depends(auth.oauth2_scheme)])
async def uploadProject(file: UploadFile, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)

    # create git repo
    project_uuid = str(uuid.uuid4())
    if not git.create_repo(project_uuid):
        return False

    # upload content from zip file
    zip_bytes_io = BytesIO(await file.read())
    try:
        with zipfile.ZipFile(zip_bytes_io, 'r', zipfile.ZIP_DEFLATED) as zipped:
            for f in zipped.infolist():
                if f.filename[-1] == "/" or not f.filename.startswith("code/"):
                    continue
                if not git.add_file(project_uuid, f.filename.split("/", 1)[1], zipped.read(f.filename)):
                    git.remove_repo(project_uuid)
                    return False

            # create db project entry
            meta = json.loads(zipped.read("meta.json"))
            if user.role == "pupil":
                new_project = models_and_schemas.Project(uuid=project_uuid, name=meta["name"],
                                                         description=meta["description"], owner_id=user.id)
            else:
                new_project = models_and_schemas.Project(uuid=project_uuid, name=meta.get("name", "__no_title__"),
                                                         description=meta.get("description", ""), owner_id=user.id, computation_time=meta.get("computation_time", 10))

            if not crud.create_project(db=db, project=new_project):
                # delete git repo
                git.remove_repo(project_uuid=project_uuid)
                return False
    except:
        git.remove_repo(project_uuid=project_uuid)
        return False

    return True
