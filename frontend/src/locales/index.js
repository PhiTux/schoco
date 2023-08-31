import home_de from "./de/home.json" 
import navbar_de from "./de/navbar.json"
import login_de from "./de/login.json"

import login_en from "./en/login.json"

const de = {
    ...login_de,
    ...home_de,
    ...navbar_de,
}

const en = {
    ...login_en,
}


export const defaultLocale = 'en'

export const languages = {
    de: de,
    en: en,
}