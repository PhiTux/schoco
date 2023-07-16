import { createApp, markRaw } from 'vue'
import { createPinia } from 'pinia'
import { router } from './router'
import App from './App.vue'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import { VAceEditor } from 'vue3-ace-editor';
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon, FontAwesomeLayers } from '@fortawesome/vue-fontawesome'
import { faUser, faUsers, faKey, faRightFromBracket, faHammer, faPlay, faEyeSlash, faEye, faLock, faSignature, faUserPlus, faCheck, faCircle, faPlus, faXmark, faTrash, faFileCirclePlus, faFolderPlus, faFloppyDisk, faArrowRotateLeft, faArrowRotateRight, faGear, faCirclePlay, faListCheck, faFolderOpen, faFile, faPencil, faShareNodes, faCircleQuestion, faSquare, faSquareCheck, faBars, faCopy, faDownload, faUpload, faListUl, faCircleCheck, faTriangleExclamation, faSearch, faCircleHalfStroke, faSun, faMoon } from '@fortawesome/free-solid-svg-icons'

library.add(faUser, faUsers, faKey, faRightFromBracket, faHammer, faPlay, faEyeSlash, faEye, faLock, faSignature, faUserPlus, faCheck, faCircle, faPlus, faXmark, faTrash, faFileCirclePlus, faFolderPlus, faFloppyDisk, faArrowRotateLeft, faArrowRotateRight, faGear, faCirclePlay, faListCheck, faFolderOpen, faFile, faPencil, faShareNodes, faCircleQuestion, faSquare, faSquareCheck, faBars, faCopy, faDownload, faUpload, faListUl, faCircleCheck, faTriangleExclamation, faSearch, faCircleHalfStroke, faSun, faMoon)

const pinia = createPinia()
pinia.use(({ store }) => {
    store.$router = markRaw(router)
})

//component('VueDatePicker', VueDatePicker)
createApp(App).use(pinia).use(router).component('v-ace-editor', VAceEditor).component('font-awesome-icon', FontAwesomeIcon).component('font-awesome-layers', FontAwesomeLayers).mount('#app')
