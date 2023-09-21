import {general_de} from "./de/general.js"
import {home_de} from "./de/home.js" 
import {navbar_de} from "./de/navbar.js"
import {login_de} from "./de/login.js"
import {new_project_de} from "./de/new_project.js"
import {users_de} from "./de/users.js"
import {homework_de} from "./de/homework.js"

import login_en from "./en/login.json"

const de = {
    ...general_de,
    ...home_de,
    ...navbar_de,
    ...login_de,
    ...new_project_de,
    ...users_de,
    ...homework_de,
}

const en = {
    ...general_de,
    ...home_de,
    ...navbar_de,
    ...login_en,
}


export const defaultLocale = 'en'

export const languages = {
    de: de,
    en: en,
}