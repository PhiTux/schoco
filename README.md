> 🛠️️ This project is pre-alpha and under heavy development! It's planned to have it 'finished' by ~September 2023


# What is schoco? {🍫}

SCHOCO stands for **SCH**ool **O**nline **CO**ding.

The project is heavily inspired by [codeboard.io](https://codeboard.io) ([github](https://github.com/codeboardio)). Since codeboard didn't receive any more updates since end of 2015 and as we need slightly other features, we now try to create a similar web-based IDE which fits to our needs for **learning (Java)-Programming explicitly at School**! 

---
It is mainly developed to enable coding-homeworks for pupils what has failed so far in reality for two reasons:
 1. Installation of the cumbersome JRE and IDEs
 2. Saving and sharing the solutions via Mail/USB/Messenger??? WTF!?
---

## Planned main-features
- No registration methods for pupils. Only teachers can register pupils who will always be part of a class or course.
- Pupils see coding-homeworks when logging in and they can code, compile, run and commit their homework completely online without the need of an offline installation of the JRE or any other software.
- JUnit for automatic testing of the commited homework
- Teachers can open pupils solutions with a single click and show/compare them at the beamer in the classroom without sending directories or files.
- Explicitly no possibility to open foreign projects based on a project-id or similar (other than codeboard!). That's first because of privacy-reasons and second to minimize copying from others.
- Use gitea on backend for storing all code.
- Compilation and running the programms completely on the server.


# Start developing

## 1) Gitea
You have to use Gitea as git-repo, since schoco uses the gitea-API.

Install gitea using the docker-compose.yml file from this repo. You can choose to set gitea public available via browser, but actually that's not necessary and you can skip reverse-proxying gitea -> it's enough to have it only available at localhost.

If you used the docker-compose.yml from this repo, then you'll need to do a second step **only once for installation**. Run the following command to create the git-user (adapt username and password):
`docker exec --user 1000 gitea gitea admin user create --admin --username schoco --password schoco1234 --email schoco@example.com`

## 2) Frontend (Vite 4 + Vue 3)
`cd frontend` 

Initial Installation: `npm install`

On every start: `npm run dev`

## 3) Backend (Fastapi)

`cd fastapi`

Initial Installation (Python 3.10 and pip required): `pip install -r requirements.txt`

On every start: `export SECRET_KEY=secret TEACHER_KEY=teacherkey && python -m uvicorn main:schoco --reload`
