import json
from sqlmodel import Session, select
from sqlalchemy import exc
import auth
import models_and_schemas
import git


def create_user(db: Session, user: models_and_schemas.UserSchema):
    hashed_password = auth.create_password_hash(user.password)
    db_user = models_and_schemas.User(
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def create_course(db: Session, course: models_and_schemas.Course):
    try:
        db.add(course)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_course_by_coursename(db: Session, coursename: str):
    course = db.query(models_and_schemas.Course).filter(
        models_and_schemas.Course.name == coursename).first()
    return course


def get_course_by_id(db: Session, id: int):
    course = db.exec(select(models_and_schemas.Course).where(
        models_and_schemas.Course.id == id)).first()
    return course


def get_user_by_username(db: Session, username: str):
    user = db.exec(select(models_and_schemas.User).where(
        models_and_schemas.User.username == username)).first()
    return user


def get_user_by_id(db: Session, id: int):
    return db.get(models_and_schemas.User, id)


def change_password_by_username(username: str, password: str, db: Session):
    try:
        db.query(models_and_schemas.User).filter(models_and_schemas.User.username ==
                                                 username).update({'hashed_password': auth.create_password_hash(password)})
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_all_users(db: Session):
    users = db.query(models_and_schemas.User).all()
    return users


def get_all_courses(db: Session):
    courses = db.exec(select(models_and_schemas.Course)).all()
    return courses


def create_UserCourseLink(db: Session, link: models_and_schemas.UserCourseLink):
    try:
        db.add(link)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_user_course_link(db: Session, link: models_and_schemas.UserCourseLink):
    link = db.query(models_and_schemas.UserCourseLink).filter(models_and_schemas.UserCourseLink.course_id ==
                                                              link.course_id, models_and_schemas.UserCourseLink.user_id == link.user_id).first()
    return link


def remove_UserCourseLink(db: Session, link: models_and_schemas.UserCourseLink):
    try:
        db.delete(link)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def remove_user(db: Session, user: models_and_schemas.User):
    try:
        # if teacher: remove homework, editingHomework, projects
        if user.role == "teacher":
            # get all projects
            projects = db.exec(select(models_and_schemas.Project).where(
                models_and_schemas.Project.owner_id == user.id)).all()
            # remove homeworks of projects
            for p in projects:
                homework = db.exec(select(models_and_schemas.Homework).where(
                    models_and_schemas.Homework.template_project_id == p.id)).first()
                if homework is None:
                    continue
                # remove editingHomeworks of homework
                editingHomeworks = db.exec(select(models_and_schemas.EditingHomework).where(
                    models_and_schemas.EditingHomework.homework_id == homework.id)).all()
                for eh in editingHomeworks:
                    db.delete(eh)
                db.delete(homework)

            # remove projects
            for p in projects:
                # remove git repo
                if not git.remove_repo(p.uuid):
                    raise Exception("Failed to remove git repo")
                db.delete(p)

        else:
            # remove editingHomework
            editingHomeworks = db.exec(select(models_and_schemas.EditingHomework).where(
                models_and_schemas.EditingHomework.owner_id == user.id)).all()
            for eh in editingHomeworks:
                # get homework
                homework = db.exec(select(models_and_schemas.Homework).where(
                    models_and_schemas.Homework.id == eh.homework_id)).first()
                # get template project
                template_project = db.exec(select(models_and_schemas.Project).where(
                    models_and_schemas.Project.id == homework.template_project_id)).first()

                # remove git branch
                if not git.remove_branch(uuid=template_project.uuid, branch=user.id):
                    raise Exception("Failed to remove git branch")

                db.delete(eh)

            # remove projects
            projects = db.exec(select(models_and_schemas.Project).where(
                models_and_schemas.Project.owner_id == user.id)).all()
            for p in projects:
                # remove git repo
                if not git.remove_repo(p.uuid):
                    raise Exception("Failed to remove git repo")
                db.delete(p)

            # remove user-course links
            userCourseLinks = db.exec(select(models_and_schemas.UserCourseLink).where(
                models_and_schemas.UserCourseLink.user_id == user.id)).all()
            for ucl in userCourseLinks:
                db.delete(ucl)

        db.delete(user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def remove_course(db: Session, course_id: int):
    try:
        # remove user-course links
        userCourseLinks = db.exec(select(models_and_schemas.UserCourseLink).where(
            models_and_schemas.UserCourseLink.course_id == course_id)).all()
        for ucl in userCourseLinks:
            db.delete(ucl)

        # remove homeworks and template-projects (including git repos)
        homeworks = db.exec(select(models_and_schemas.Homework).where(
            models_and_schemas.Homework.course_id == course_id)).all()
        for h in homeworks:
            # remove git repo
            template_project = db.exec(select(models_and_schemas.Project).where(
                models_and_schemas.Project.id == h.template_project_id)).first()
            if not git.remove_repo(template_project.uuid):
                raise Exception(
                    f"Failed to remove git repo {template_project.uuid}")
            # remove project
            db.delete(template_project)

            # remove editing_homework
            editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
                models_and_schemas.EditingHomework.homework_id == h.id)).first()
            db.delete(editing_homework)

            # remove homework
            db.delete(h)

        # remove course
        course = db.exec(select(models_and_schemas.Course).where(
            models_and_schemas.Course.id == course_id)).first()
        db.delete(course)

        # db.delete(course)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def change_name(db: Session, user_id: str, name: str):
    user = get_user_by_id(db=db, id=user_id)
    user.full_name = name
    try:
        db.add(user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def change_username(db: Session, user_id: str, name: str):
    user = get_user_by_id(db=db, id=user_id)
    user.username = name
    try:
        db.add(user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def create_project(db: Session, project: models_and_schemas.Project):
    try:
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def remove_project_by_uuid(db: Session, project_uuid: str):
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.uuid == project_uuid)).first()
    try:
        db.delete(project)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def delete_solution_project_by_project_id(db: Session, project_id: int):
    # check all homeworks, if they have this project as solution
    homeworks = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.solution_project_id == project_id)).all()

    for h in homeworks:
        if not delete_solution_from_homework(db, h):
            return False
    return True


def delete_solution_from_homework(db: Session, homework: models_and_schemas.Homework):
    homework.solution_project_id = None
    homework.solution_start_showing = None
    try:
        db.add(homework)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_project_by_project_uuid(db: Session, project_uuid: str):
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.uuid == project_uuid)).first()
    return project


def get_project_by_id(db: Session, id: int):
    return db.get(models_and_schemas.Project, id)


def get_projects_by_ids(db: Session, ids: list[int]):
    return db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.id.in_(ids))).all()


def get_projects_by_username(db: Session, username: str):
    owner = db.exec(select(models_and_schemas.User).where(
        models_and_schemas.User.username == username)).first()
    projects = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.owner == owner)).all()
    return projects


def update_description(db: Session, project_uuid: str, description: str):
    try:
        project = db.exec(select(models_and_schemas.Project).where(
            models_and_schemas.Project.uuid == project_uuid)).first()
        project.description = description
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def update_project_name(db: Session, project_uuid: str, name: str):
    try:
        project = db.exec(select(models_and_schemas.Project).where(
            models_and_schemas.Project.uuid == project_uuid)).first()
        project.name = name
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def create_homework(db: Session, homework: models_and_schemas.Homework):
    try:
        db.add(homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_teachers_homework_by_username(db: Session, username: str):
    """return all homework, that was created (!) by given username"""
    # get my project_ids
    project_ids = db.exec(select(models_and_schemas.Project.id).join(
        models_and_schemas.User).where(models_and_schemas.User.username == username)).all()
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.template_project_id.in_(project_ids))).all()
    return homework


def get_pupils_homework_by_username(db: Session, username: str):
    """return all homework, which is posted for courses that I attend"""
    courses = get_courses_by_username(db=db, username=username)
    course_ids = []
    for c in courses:
        course_ids.append(c.id)

    results = []
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.course_id.in_(course_ids))).all()
    for h in homework:
        project = get_project_by_id(db=db, id=h.template_project_id)
        results.append({"deadline": h.deadline, "id": h.id,
                       "name": project.name, "description": project.description, "uuid": project.uuid, "solution_project_id": h.solution_project_id, "solution_start_showing": h.solution_start_showing})

    return results


def get_courses_by_username(db: Session, username: str):
    user = db.exec(select(models_and_schemas.User).where(
        models_and_schemas.User.username == username)).first()
    return user.courses


def get_homework_by_courses(db: Session, courses: list[models_and_schemas.Course]):
    courses_ids = []
    for c in courses:
        courses_ids.append(c.id)
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.course_id.in_(courses_ids))).all()
    return homework


def get_editing_homework_by_username(db: Session, username: str):
    user = get_user_by_username(db, username)
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.owner == user)).all()
    return editing_homework


def get_homework_by_id(db: Session, id: int):
    return db.get(models_and_schemas.Homework, id)


def create_editing_homework(db: Session, editing_homework: models_and_schemas.EditingHomework):
    try:
        db.add(editing_homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_template_project_of_editing_homework_by_uuid(db: Session, project_uuid: str):
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.uuid == project_uuid)).first()
    project = get_project_by_id(
        db=db, id=editing_homework.homework.template_project_id)
    return project


def get_editing_homework_by_uuid_and_user_id(db: Session, uuid: str, user_id: int):
    template_project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.uuid == uuid)).first()
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.template_project_id == template_project.id)).first()
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.homework == homework, models_and_schemas.EditingHomework.owner_id == user_id)).first()
    return editing_homework


def get_all_users_of_course_id(db: Session, id: str):
    course = db.exec(select(models_and_schemas.Course).where(
        models_and_schemas.Course.id == id)).first()
    return course.users


def get_all_editing_homework_by_homework_id(db: Session, id: str):
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.homework_id == id)).all()
    return editing_homework


""" def get_template_project_of_homework_by_id(db: Session, homework_id: int):
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.id == homework_id)).first()
    template_project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.id == homework.template_project_id)).first()
    return template_project """


def get_uuid_of_homework(db: Session, homework_id: int):
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.id == homework_id)).first()
    template_project = get_project_by_id(
        db=db, id=homework.template_project_id)
    return template_project.uuid


def increase_compiles(db: Session, uuid: str, user_id: int):
    editing_homework = get_editing_homework_by_uuid_and_user_id(
        db=db, uuid=uuid, user_id=user_id)
    editing_homework.number_of_compilations += 1

    try:
        db.add(editing_homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def increase_runs(db: Session, uuid: str, user_id: int):
    editing_homework = get_editing_homework_by_uuid_and_user_id(
        db=db, uuid=uuid, user_id=user_id)
    editing_homework.number_of_runs += 1

    try:
        db.add(editing_homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def increase_tests(db: Session, uuid: str, user_id: int):
    editing_homework = get_editing_homework_by_uuid_and_user_id(
        db=db, uuid=uuid, user_id=user_id)
    editing_homework.number_of_tests += 1

    try:
        db.add(editing_homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_homework_by_template_uuid(db: Session, uuid: str):
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.uuid == uuid)).first()
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.template_project_id == project.id)).first()
    return homework


def save_test_result(db: Session, uuid: str, user_id: int, result: dict):
    editing_homework = get_editing_homework_by_uuid_and_user_id(
        db=db, uuid=uuid, user_id=user_id)
    editing_homework.submission = json.dumps({
        'passed_tests': result['passed_tests'], 'failed_tests': result['failed_tests']})

    try:
        db.add(editing_homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def remove_all_editing_homework_by_homework_id(db: Session, id: int):
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.homework_id == id)).all()
    for eh in editing_homework:
        db.delete(eh)
    try:
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def remove_homework_by_id(db: Session, id: int):
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.id == id)).first()
    db.delete(homework)
    try:
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def remove_editing_homework_by_uuid_and_user_id(db: Session, uuid: str, user_id: int):
    editing_homework = get_editing_homework_by_uuid_and_user_id(
        db=db, uuid=uuid, user_id=user_id)
    db.delete(editing_homework)
    try:
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def rename_homework(db: Session, id: int, new_name: str):
    template_project_id = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.id == id)).first().template_project_id
    template_project = get_project_by_id(db, template_project_id)
    template_project.name = new_name
    try:
        db.add(template_project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def rename_project(db: Session, uuid: str, new_name: str):
    project = get_project_by_project_uuid(db, uuid)
    project.name = new_name
    try:
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def edit_course(db: Session, course: models_and_schemas.Course):

    course_to_edit = db.exec(select(models_and_schemas.Course).where(
        models_and_schemas.Course.id == course.id)).first()
    course_to_edit.name = course.name
    course_to_edit.color = course.color
    course_to_edit.fontDark = course.fontDark

    try:
        db.add(course_to_edit)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_template_project_by_homework_id(db: Session, id: int):
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.id == id)).first()
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.id == homework.template_project_id)).first()
    return project


def update_computation_time(db: Session, id: int, computation_time: int):
    # get template project
    template_project = get_template_project_by_homework_id(db, id)
    if template_project is None:
        return False

    # update computation time
    template_project.computation_time = computation_time
    try:
        db.add(template_project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def update_deadline(db: Session, id: int, deadline: int):
    # get homework
    homework = get_homework_by_id(db, id)
    if homework is None:
        return False

    # update deadline
    homework.deadline = deadline
    try:
        db.add(homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_courses_of_homework_by_original_uuid(db: Session, original_project_id: int):
    homeworks = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.original_project_id == original_project_id)).all()

    if not len(homeworks):
        return []

    allCourses = get_all_courses(db=db)

    homeworkCourses = []
    for h in homeworks:
        for c in allCourses:
            if c.id == h.course_id:
                homeworkCourses.append(c)
                break

    return homeworkCourses


def add_solution(db: Session, homework_id: int, solution_id: int, solution_start_showing: str):
    if solution_id is None or solution_id == 0 or solution_start_showing == "" or homework_id == 0:
        return False

    # get homework
    homework = get_homework_by_id(db, homework_id)
    if homework is None:
        return False

    # update solution
    homework.solution_project_id = solution_id
    homework.solution_start_showing = solution_start_showing
    try:
        db.add(homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def check_if_uuid_is_solution(db: Session, uuid: str):
    # get project
    project = get_project_by_project_uuid(db, uuid)
    if project is None:
        return False

    # get homework
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.solution_project_id == project.id)).first()
    if homework is None:
        return False

    return True


def get_entry_point_by_project_uuid(db: Session, project_uuid: str):
    # get project
    project = get_project_by_project_uuid(db, project_uuid)
    if project is None:
        return ""

    return project.main_class


def set_entry_point_by_project_uuid(db: Session, project_uuid: str, entry_point: str):
    # add slash to end if missing
    if entry_point[-1] != "/":
        entry_point += "/"

    # get project
    project = get_project_by_project_uuid(db, project_uuid)
    if project is None:
        return False

    # update entry point
    project.main_class = entry_point
    try:
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True
