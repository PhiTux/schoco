import { createApp, markRaw } from 'vue'
import { createPinia } from 'pinia'
import { router } from './router'
import App from './App.vue'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faUser, faUsers, faKey, faRightFromBracket, faHammer, faPlay, faEyeSlash, faEye } from '@fortawesome/free-solid-svg-icons'

library.add(faUser, faUsers, faKey, faRightFromBracket, faHammer, faPlay, faEyeSlash, faEye)

const pinia = createPinia()
pinia.use(({store}) => {
    store.$router = markRaw(router)
})

createApp(App).use(router).use(pinia).component('font-awesome-icon', FontAwesomeIcon).mount('#app')
