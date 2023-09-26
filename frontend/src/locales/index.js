import {general_de} from "./de/general.js"
import {home_de} from "./de/home.js" 
import {navbar_de} from "./de/navbar.js"
import {login_de} from "./de/login.js"
import {new_project_de} from "./de/new_project.js"
import {users_de} from "./de/users.js"
import {homework_de} from "./de/homework.js"
import { color_mode_switch_de } from "./de/color_mode_switch.js"
import { password_info_de } from "./de/password_info.js"
import { project_card_de } from "./de/project_card.js"
import { ide_de } from "./de/ide.js"

import login_en from "./en/login.json"

const de = {
    ...general_de,
    ...home_de,
    ...navbar_de,
    ...login_de,
    ...new_project_de,
    ...users_de,
    ...homework_de,
    ...color_mode_switch_de,
    ...password_info_de,
    ...project_card_de,
    ...ide_de,
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