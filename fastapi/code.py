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
import datetime

code = APIRouter(prefix="/api")

#CODE_PATH = "code/"
DEFAULT_COMPUTATION_TIME = 10


@code.post('/createNewHelloWorld', dependencies=[Depends(auth.oauth2_scheme)])
def createNewHelloWorld(newProject: models_and_schemas.newProject, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):

    if newProject.projectName.strip() == "":
        raise HTTPException(status_code=400, detail="Project name empty")

    project_uuid = str(uuid.uuid4())
    user = crud.get_user_by_username(db=db, username=username)
    project = models_and_schemas.Project(
        name=newProject.projectName, description=newProject.projectDescription, uuid=project_uuid, owner_id=user.id, computation_time=DEFAULT_COMPUTATION_TIME, main_class="Schoco.java/")

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

        # ... or he is trying to open a solution
        if check_if_solution(db=db, project_uuid=project_uuid, username=username):
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


def check_if_solution(db: Session, project_uuid: str, username: str):
    """Returns True if project_uuid is a solution-project AND (!) if user is NOT owner, otherwise False"""
    return crud.check_if_uuid_is_solution(db=db, uuid=project_uuid) and crud.get_project_by_project_uuid(db=db, project_uuid=project_uuid).owner.username != username


results = []


def recursively_download_all_files(project_uuid: str, id: int, path: str, is_solution: bool = False):
    global results

    root = git.load_all_meta_content(
        project_uuid=project_uuid, id=id, path=path)

    # download all files
    for c in root:
        if not c['isDir']:
            # skip Tests.java if it's a pupil's-branch
            if (id != 0 or is_solution) and c['path'] == 'Tests.java':
                continue
            results.append({'path': c['path'], 'content': git.download_file_by_url(
                url=git.replace_base_url(c['download_url'])), 'sha': c['sha']})
        else:
            recursively_download_all_files(
                project_uuid=project_uuid, id=id, path=f"/{c['path']}/", is_solution=is_solution)

    return (results)


@ code.get('/loadAllFiles/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def loadAllFiles(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    global results
    results = []

    is_solution = check_if_solution(
        db=db, project_uuid=project_uuid, username=username)

    res = recursively_download_all_files(
        project_uuid=project_uuid, id=user_id, path="/", is_solution=is_solution)

    entry_point = crud.get_entry_point_by_project_uuid(
        db=db, project_uuid=project_uuid)

    return {'files': res, 'entry_point': entry_point}


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
def getProjectName(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)

    homework = crud.get_homework_by_template_uuid(db=db, uuid=project_uuid)
    isHomework = True
    if homework == None:
        isHomework = False

    is_solution = check_if_solution(
        db=db, project_uuid=project_uuid, username=username)

    result = {"name": project.name,
              "description": project.description, "isHomework": isHomework, "isSolution": is_solution}

    if isHomework and user_id != 0:
        user = crud.get_user_by_id(db=db, id=user_id)
        result['fullusername'] = user.full_name
        result['deadline'] = homework.deadline
        result['id'] = homework.id

    return result


@ code.post('/saveFileChanges/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def saveFileChanges(fileChanges: models_and_schemas.FileChangesList, project_uuid: str = Path(), user_id: int = Path()):

    success = []
    for f in fileChanges.changes:
        res = git.update_file(project_uuid, user_id, f.path, f.content, f.sha)
        if res:
            success.append(
                {'path': f.path, 'content': f.content, 'sha': res['sha']})

    # remove .class files (they are now outdated)
    cookies_api.remove_compilation_result(f"{project_uuid}_{user_id}")

    return success


def calc_all_submissions(editing_homework: list[models_and_schemas.EditingHomework]):
    passed_tests = 0
    failed_tests = 0
    for e in editing_homework:
        if e.submission != "":
            submission = json.loads(e.submission)
            passed_tests += submission["passed_tests"]
            failed_tests += submission["failed_tests"]
    return '{"passed_tests":' + str(passed_tests) + ', "failed_tests": ' + str(failed_tests) + '}'


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

                solution_project = crud.get_project_by_id(
                    db=db, id=h.solution_project_id)
                if solution_project == None:
                    solution_name = ""
                else:
                    solution_name = solution_project.name

                # get amount of pupils, that are editing this homework
                editing_homework = crud.get_all_editing_homework_by_homework_id(
                    db=db, id=h.id)
                pupils_editing = len(editing_homework)
                # get amount of pupils, that are in the course
                pupils_in_course = len(
                    crud.get_all_users_of_course_id(db=db, id=h.course_id))

                submission = calc_all_submissions(editing_homework)

                homework.append({"deadline": h.deadline, "name": p.name, "description": p.description, "id": h.id,
                                "course_id": h.course_id, "course_name": course.name, "course_color": course.color, "course_font_dark": course.fontDark,
                                 "solution_name": solution_name, "solution_id": 0 if h.solution_project_id == None else h.solution_project_id, "solution_start_showing": h.solution_start_showing,
                                 "pupils_editing": pupils_editing, "pupils_in_course": pupils_in_course, "submission": submission})
                # TODO append "edited by X/Y pupils" and "average points of solutions"
                break

        # ...otherwise its a regular project
        if not is_homework:
            projects.append(
                {"name": p.name, "description": p.description, "uuid": p.uuid, "id": p.id})

    return {"homework": homework, "projects": projects}


def get_solution_project_uuid(db, homework):
    if homework["solution_project_id"] == None:
        return ""

    # check if solution_start_showing has passed -> solution may be shown
    try:
        if datetime.datetime.strptime(homework["solution_start_showing"], '%Y-%m-%dT%H:%M:%S.%fZ') > datetime.datetime.utcnow():
            return ""
    # if solution_start_showing is broken, then solution may be shown
    except ValueError:
        print("Timecode error of solution_start_showing")

    # get solution project uuid
    return crud.get_project_by_id(
        db=db, id=homework["solution_project_id"]).uuid


@code.get('/getProjectsAsPupil')
def getProjectsAsPupil(db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)

    all_projects = crud.get_projects_by_username(db=db, username=username)

    all_editing_homework = crud.get_editing_homework_by_username(
        db=db, username=username)

    all_homework = crud.get_pupils_homework_by_username(
        db=db, username=username)

    homework = []

    for h in all_homework:
        already_edited = False

        # check if solution may be shown
        solution_uuid = get_solution_project_uuid(db, h)

        for e in all_editing_homework:
            if h["id"] == e.homework_id:
                # append those homeworks, that are already edited
                already_edited = True
                uuid = crud.get_uuid_of_homework(
                    db=db, homework_id=h['id'])

                homework.append({"is_editing": True, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                                "id": h["id"], "uuid": uuid, "branch": user.id, "solution_uuid": solution_uuid, "submission": e.submission})
                break
        # ... and those, which are not yet started by the pupil
        if not already_edited:
            homework.append({"is_editing": False, "deadline": h["deadline"], "name": h["name"], "description": h["description"],
                             "id": h["id"], "solution_uuid": solution_uuid, "submission": ""})

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
        startCompile.container_uuid, startCompile.port, computation_time, startCompile.save_output)

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

    entry_point = crud.get_entry_point_by_project_uuid(
        db=db, project_uuid=project_uuid)

    # remove everything behind last dot
    entry_point = entry_point[:entry_point.rfind('.')]

    result = cookies_api.start_execute(
        startExecute.container_uuid, startExecute.port, computation_time, startExecute.save_output, entry_point)

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

    background_tasks.add_task(
        cookies_api.kill_n_create, startTest.container_uuid)

    if "status" in result and result["status"] == "connect_error":
        return result

    if user_id != 0 and not ("status" in result and result["status"] == "security_error"):
        crud.increase_tests(db=db, uuid=project_uuid, user_id=user_id)
        if not (result['passed_tests'] == 0 and result['failed_tests'] == 0):
            crud.save_test_result(db=db, uuid=project_uuid,
                                  user_id=user_id, result=result)

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
        uuid=template_project_uuid, name=project.name, description=project.description, owner_id=project.owner_id, computation_time=create_homework.computation_time, main_class=project.main_class)
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
              "course_color": homework.course.color, "course_font_dark": homework.course.fontDark, "deadline": homework.deadline, "computation_time": template_project.computation_time}

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
                                  "result": "", "compilations": 0, "runs": 0, "tests": 0})

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

        # remove project from homework-solution (if it is one)
        if not crud.delete_solution_project_by_project_id(db=db, project_id=project.id):
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
    if file.new_path.strip() == "" or " " in file.new_path.strip():
        raise HTTPException(
            status_code=400, detail="Wrong input: New path is invalid.")

    if not git.renameFile(file.old_path, file.new_path, project_uuid, user_id, file.content, file.sha):
        raise HTTPException(
            status_code=500, detail="Error on renaming file.")

    # update entry_point if old_path was entry_point
    entry_point = crud.get_entry_point_by_project_uuid(
        db=db, project_uuid=project_uuid)
    print(entry_point, file.old_path)

    if entry_point == file.old_path or entry_point == file.old_path + "/":
        if not crud.set_entry_point_by_project_uuid(db=db, project_uuid=project_uuid, entry_point=file.new_path):
            raise HTTPException(
                status_code=500, detail="Error on setting entry point.")

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


@code.post('/addEmptyFile/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def addEmptyFile(addFile: models_and_schemas.AddFile, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if addFile.path.strip() == "" or " " in addFile.path.strip():
        raise HTTPException(
            status_code=400, detail="Wrong input: Invalid Path.")

    res = git.add_empty_file(project_uuid, user_id, addFile.path)
    if not res['success']:
        raise HTTPException(
            status_code=500, detail="Error on adding file.")

    return {'success': True, 'sha': res['sha']}


@code.post('/deleteFile/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def deleteFile(deleteFile: models_and_schemas.DeleteFile, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if deleteFile.path.strip() == "" or deleteFile.sha.strip() == "":
        raise HTTPException(
            status_code=400, detail="Wrong input: Path or sha is empty.")

    if not git.delete_file(project_uuid, user_id, deleteFile.path, deleteFile.sha):
        raise HTTPException(
            status_code=500, detail="Error on deleting file.")

    return {'success': True}


@code.post('/updateHomeworkSettings', dependencies=[Depends(auth.check_teacher)])
def updateHomeworkSettings(homework: models_and_schemas.UpdateHomeworkSettings, db: Session = Depends(database_config.get_db)):
    if homework.deadline_date == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: Deadline is empty.")

    if not crud.update_template_computation_time(db=db, id=homework.id, computation_time=homework.computation_time):
        raise HTTPException(
            status_code=500, detail="Error on updating computation time.")

    if not crud.update_deadline(db=db, id=homework.id, deadline=homework.deadline_date):
        raise HTTPException(
            status_code=500, detail="Error on updating deadline.")

    return {'success': True}


@code.post('/stopContainer', dependencies=[Depends(auth.oauth2_scheme)])
def stopContainer(container_uuid: models_and_schemas.UUID, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    if not cookies_api.kill_container(container_uuid.uuid):
        raise HTTPException(
            status_code=500, detail="Error on stopping container.")

    return {'success': True}


@code.post('/addSolution', dependencies=[Depends(auth.check_teacher)])
def addSolution(addSolution: models_and_schemas.AddSolution, db: Session = Depends(database_config.get_db)):
    if not crud.add_solution(db=db, homework_id=addSolution.homework_id, solution_id=addSolution.solution_id, solution_start_showing=addSolution.solution_start_showing):
        raise HTTPException(
            status_code=500, detail="Error on adding solution.")

    return {'success': True}


@code.post('/deleteSolution', dependencies=[Depends(auth.check_teacher)])
def deleteSolution(deleteSolution: models_and_schemas.DeleteSolution, db: Session = Depends(database_config.get_db)):
    homework = crud.get_homework_by_id(db=db, id=deleteSolution.homework_id)
    if homework == None:
        raise HTTPException(
            status_code=400, detail="Wrong input: Homework not found.")

    if not crud.delete_solution_from_homework(db=db, homework=homework):
        raise HTTPException(
            status_code=500, detail="Error on deleting solution.")

    return {'success': True}


@code.get('/loadEntryPoint/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def loadEntryPoint(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    main_project_uuid = project_uuid

    if user_id != 0:
        main_project_uuid = crud.get_template_project_of_editing_homework_by_uuid(
            db, project_uuid).uuid

    entry_point = crud.get_entry_point_by_project_uuid(
        db=db, project_uuid=main_project_uuid)

    return {'entry_point': entry_point}


@code.post('/setEntryPoint/{project_uuid}/{user_id}', dependencies=[Depends(project_access_allowed)])
def setEntryPoint(entryPoint: models_and_schemas.EntryPoint, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    entry_point = entryPoint.entry_point
    if not entry_point.endswith('/'):
        entry_point += '/'

    if not crud.set_entry_point_by_project_uuid(db=db, project_uuid=project_uuid, entry_point=entry_point):
        raise HTTPException(
            status_code=500, detail="Error on setting entry point.")

    return {'success': True}


@code.get('/getTeacherComputationTime/{project_uuid}/{user_id}', dependencies=[Depends(auth.check_teacher)])
def getTeacherComputationTime(project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if (user_id != 0):
        raise HTTPException(
            status_code=405, detail="Not allowed. Only allowed to edit computation time in own projects.")

    project = crud.get_project_by_project_uuid(
        db=db, project_uuid=project_uuid)
    if project != None:
        return {'success': True, 'computation_time': project.computation_time}

    return {'success': False}


@code.post('/setTeacherComputationTime/{project_uuid}/{user_id}', dependencies=[Depends(auth.check_teacher)])
def setComputationTime(computationTime: models_and_schemas.ComputationTime, project_uuid: str = Path(), user_id: int = Path(), db: Session = Depends(database_config.get_db)):
    if (user_id != 0):
        raise HTTPException(
            status_code=405, detail="Not allowed. Only allowed to edit computation time in own projects.")

    if not crud.update_computation_time_by_project_uuid(db=db, project_uuid=project_uuid, computation_time=computationTime.computation_time):
        raise HTTPException(
            status_code=500, detail="Error on updating computation time.")

    return {'success': True}
