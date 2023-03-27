from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path
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


@code.post('/createNewHelloWorld', dependencies=[Depends(auth.oauth2_scheme)])
def createNewHelloWorld(newProject: models_and_schemas.newProject, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    project_uuid = str(uuid.uuid4())
    user = crud.get_user_by_username(db=db, username=username)
    project = models_and_schemas.Project(
        name=newProject.projectName, description=newProject.projectDescription, uuid=project_uuid, owner_id=user.id)

    # create git repo
    if not git.create_repo(project_uuid):
        raise HTTPException(status_code=500, detail="Could not create project")

    # load the template files into the git repo
    for file in os.listdir("./java_helloWorld"):
        if file.endswith(".class"):
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


def project_access_allowed(project_uuid: str, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    # teacher is allowed to open
    user = crud.get_user_by_username(db=db, username=username)
    if user.role == "teacher":
        return True

    # otherwise: user must be owner of project...
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project != None and project.owner.username == username:
        return True

    # ...or of editing_homework
    editing_homework = crud.get_editing_homework_by_uuid(
        db=db, project_uuid=project_uuid)
    if editing_homework != None and editing_homework.owner.username == username:
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
    if project.owner.username == username:
        return True

    raise HTTPException(
        status_code=405, detail="You're not allowed to open or edit this project")


results = []


def recursively_download_all_files(project_uuid: str, path: str):
    global results

    root = git.load_all_meta_content(
        project_uuid=project_uuid, path=path)

    # download all files
    for c in root:
        if not c['isDir']:
            print(c)
            results.append({'path': c['path'], 'content': git.download_file_by_url(
                url=git.replace_base_url(c['download_url'])), 'sha': c['sha']})
        else:
            recursively_download_all_files(
                project_uuid=project_uuid, path=f"/{c['path']}/")

    return (results)


@ code.get('/loadAllFiles/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def loadAllFiles(project_uuid: str = Path(), db: Session = Depends(database_config.get_db)):
    global results
    results = []

    res = recursively_download_all_files(project_uuid=project_uuid, path="/")

    # remove Tests.java if uuid is "editing_homework"
    editing_homework = crud.get_editing_homework_by_uuid(
        db=db, project_uuid=project_uuid)
    if editing_homework != None:
        res = [f for f in res if not f['path'] == "Tests.java"]

    return res


@ code.post('/updateDescription/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def saveDescription(updateDescription: models_and_schemas.updateDescription, project_uuid: str = Path(), db: Session = Depends(database_config.get_db)):
    result = crud.update_description(
        db=db, project_uuid=project_uuid, description=updateDescription.description)
    return result


@ code.get('/getProjectInfo/{project_uuid}', dependencies=[Depends(auth.oauth2_scheme)])
def getProjectName(project_uuid: str = Path(), db: Session = Depends(database_config.get_db)):
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project != None:
        return {"name": project.name, "description": project.description, "isEditingHomework": False}
    else:
        project = crud.get_template_project_of_editing_homework_by_uuid(
            db=db, project_uuid=project_uuid)
        return {"name": project.name, "description": project.description, "isEditingHomework": True}


@ code.post('/saveFileChanges/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def saveFileChanges(fileChanges: models_and_schemas.FileChangesList, project_uuid: str = Path()):

    success = []
    for f in fileChanges.changes:
        res = git.update_file(project_uuid, f.path, f.content, f.sha)
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
                homework.append({"is_editing": True, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                                "id": h["id"], "uuid": e.uuid, "oldest_commit_allowed": h["oldest_commit_allowed"]})
                break
        # ... and those, which are not yet started by the pupil
        if not already_edited:
            homework.append({"is_editing": False, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                             "id": h["id"], "uuid": h["uuid"], "oldest_commit_allowed": h["oldest_commit_allowed"]})

    return {"homework": homework, "projects": all_projects}


@ code.post('/prepareCompile/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def prepareCompile(prepareCompile: models_and_schemas.prepareCompile, project_uuid: str = Path()):

    # write files to container-mount and return WS-URL
    c = cookies_api.prepareCompile(prepareCompile.files)

    return c


@ code.post('/startCompile/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def startCompile(startCompile: models_and_schemas.startCompile, background_tasks: BackgroundTasks, project_uuid: str = Path()):

    result = cookies_api.startCompile(
        startCompile.container_uuid, startCompile.ip, startCompile.port)

    # save compilation-results (.class-files)
    cookies_api.save_compilation_result(
        startCompile.container_uuid, project_uuid)

    # before return: start background_task to refill new_containers
    background_tasks.add_task(
        cookies_api.kill_n_create, startCompile.container_uuid)

    return result


@ code.get('/prepareExecute/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def prepareExecute(project_uuid: str = Path()):

    # prepares container by copying .class files into container-mount
    # returns {'executable': false} if no files are found
    c = cookies_api.prepare_execute(project_uuid)
    return c


@ code.post('/startExecute/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def startExecute(startExecute: models_and_schemas.startExecute, background_tasks: BackgroundTasks, project_uuid: str = Path()):

    result = cookies_api.start_execute(
        startExecute.container_uuid, startExecute.ip, startExecute.port)

    background_tasks.add_task(
        cookies_api.kill_n_create, startExecute.container_uuid)

    return result


@ code.get('/prepareTest/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def prepareTest(project_uuid: str = Path()):
    # we now use "prepare_execute", since it is (at least until now) the same code
    c = cookies_api.prepare_execute(project_uuid)
    return c


@ code.post('/startTest/{project_uuid}', dependencies=[Depends(project_access_allowed)])
def startTest(startTest: models_and_schemas.startTest, background_tasks: BackgroundTasks, project_uuid: str = Path()):

    result = cookies_api.start_test(
        startTest.container_uuid, startTest.ip, startTest.port)

    background_tasks.add_task(
        cookies_api.kill_n_create, startTest.container_uuid)

    return result


@ code.post('/createHomework/{project_uuid}', dependencies=[Depends(project_access_allowed_teacher_only)])
def createHomework(create_homework: models_and_schemas.create_homework, project_uuid: str = Path(), db: Session = Depends(database_config.get_db)):

    orig_project_uuid = project_uuid
    template_project_uuid = str(uuid.uuid4())

    # fork original gitea project to create template for the homework
    if not git.forkProject(
            orig_project_uuid=orig_project_uuid, fork_project_uuid=template_project_uuid):
        return False

    print("template", template_project_uuid)

    # copy project-entry in database
    project = crud.get_project_by_project_uuid(db, orig_project_uuid)
    if project == None:
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    original_project_id = project.id

    #project.uuid = template_project_uuid
    new_project = models_and_schemas.Project(
        uuid=template_project_uuid, name=project.name, description=project.description, owner_id=project.owner_id)
    if not crud.create_project(db=db, project=new_project):
        # delete git repo
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    # prepare to create DB-entry
    p = crud.get_project_by_project_uuid(db, template_project_uuid)
    template_project_id = p.id

    # get most recent commit-sha
    commit = git.get_recent_commit_by_project_uuid(template_project_uuid)
    if commit == 0:
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    homework = models_and_schemas.Homework(course_id=create_homework.course_id, template_project_id=template_project_id,
                                           original_project_id=original_project_id, deadline=create_homework.deadline_date, computation_time=create_homework.computation_time, oldest_commit_allowed=commit)
    print(homework)
    if not crud.create_homework(db,
                                homework=homework):
        git.remove_repo(project_uuid=template_project_uuid)
        return False

    return True


@code.post('/startHomework', dependencies=[Depends(auth.oauth2_scheme)])
def startHomework(homeworkId: models_and_schemas.homeworkId, username=Depends(auth.get_username_by_token), db: Session = Depends(database_config.get_db)):
    id = homeworkId.id

    # check if editing_homework from user for given homework-id already exists
    editing_homeworks = crud.get_editing_homework_by_username(
        db=db, username=username)
    for h in editing_homeworks:
        if h.id == id:
            raise HTTPException(
                status_code=409, detail="You're already working on this Homework.")

    # get homework
    try:
        homework = crud.get_homework_by_id(db=db, id=id)
    except:
        raise HTTPException(
            status_code=500, detail=f"Could not find homework with id {id}.")

    # get project_uuid from project_id
    template_project = crud.get_project_by_id(
        db=db, id=homework.template_project_id)

    # fork project
    new_project_uuid = str(uuid.uuid4())
    if not git.forkProject(
            orig_project_uuid=template_project.uuid, fork_project_uuid=new_project_uuid):
        raise HTTPException(
            status_code=500, detail=f"Error on starting homework with id {id}.")

    user = crud.get_user_by_username(db=db, username=username)

    # create editing_homework - otherwise remove repo
    editing_homework = models_and_schemas.EditingHomework(
        uuid=new_project_uuid, homework_id=id, owner_id=user.id)
    if not crud.create_editing_homework(db,
                                        editing_homework=editing_homework):
        git.remove_repo(project_uuid=new_project_uuid)
        raise HTTPException(
            status_code=500, detail=f"Error on starting homework with id {id}.")

    return {'success': True, 'uuid': new_project_uuid}


@code.post('/getHomeworkInfo', dependencies=[Depends(auth.check_teacher)])
def getHomeworkInfo(homeworkId: models_and_schemas.homeworkId, db: Session = Depends(database_config.get_db)):
    id = homeworkId.id

    # get project_name and course_badge_info
    homework = crud.get_homework_by_id(db=db, id=id)
    template_project = crud.get_project_by_id(
        db=db, id=homework.template_project_id)

    result = {"name": template_project.name, "course_name": homework.course.name,
              "course_color": homework.course.color, "course_font_dark": homework.course.fontDark}

    # get each user's results
    pupils = crud.get_all_users_of_course_id(db=db, id=homework.course_id)
    print(pupils)
    editing_homework = crud.get_all_editing_homework_by_homework_id(
        db=db, id=id)

    pupils_results = []
    for p in pupils:
        found = False
        for eh in editing_homework:
            if p.id == eh.owner_id:
                found = True
                pupils_results.append({"name": p.full_name, "username": p.username, "uuid": eh.uuid, "best_result": eh.best_submission,
                                      "#compilations": eh.number_of_compilations, "#runs": eh.number_of_runs, "#tests": eh.number_of_tests})
                break

        if not found:
            pupils_results.append({"name": p.full_name, "username": p.username, "uuid": "",
                                  "best_result": "", "compilations": 0, "runs": 0, "tests": 0})

    result['pupils_results'] = pupils_results

    return result
