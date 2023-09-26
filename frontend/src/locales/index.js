// german
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

// english
import {general_en} from "./en/general.js"
import {home_en} from "./en/home.js"
import {navbar_en} from "./en/navbar.js"
import {login_en} from "./en/login.js"
import {new_project_en} from "./en/new_project.js"
import {users_en} from "./en/users.js"
import {homework_en} from "./en/homework.js"
import {color_mode_switch_en} from "./en/color_mode_switch.js"
import { password_info_en } from "./en/password_info.js"
import { project_card_en } from "./en/project_card.js"
import {ide_en} from "./en/ide.js"

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
    ...general_en,
    ...home_en,
    ...navbar_en,
    ...login_en,
    ...new_project_en,
    ...users_en,
    ...homework_en,
    ...color_mode_switch_en,
    ...password_info_en,
    ...project_card_en,
    ...ide_en,
}


export const defaultLocale = 'en'

export const languages = {
    de: de,
    en: en,
}