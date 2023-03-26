import {createRouter, createWebHashHistory} from 'vue-router'
import { useAuthStore } from '../stores/auth.store.js'
import Login from "../views/Login.vue"
import Home from "../views/Home.vue"
import Users from "../views/Users.vue"
import NewProject from "../views/NewProject.vue"
import Ide from "../views/IDE.vue"
import Homework from "../views/Homework.vue"


const routes = [
    {path: '/login', name: 'login', component: Login},
    {path: '/home', name: "home", component: Home},
    {path: '/users', name: "users", component: Users},
    {path: '/newProject', name: "newProject", component: NewProject},
    {path: '/ide/:project_uuid', name: "ide", component: Ide, params: {project_uuid: ""}},
    {path: '/homework/:id', name: "homework", component: Homework, params: {id: ""}},
    {path: '/:pathMath(.*)*', redirect: "/home"}
]

export const router = createRouter({
    history: createWebHashHistory(),
    routes
})

router.beforeEach(async (to) => {
    const publicPages = ['/login']
    const authRequired = !publicPages.includes(to.path)
    const auth = useAuthStore()

    const teacherPages = ['/users', '/homework']
    const teacherRequired = teacherPages.includes(to.path)

    if (authRequired && !auth.user) {
        auth.returnUrl = to.fullPath;
        return '/login'
    }

    if (teacherRequired && (!auth.user || !auth.isTeacher())) {
        auth.returnUrl = '/home'
        return '/home'
    }

    if (to.path == '/login' && auth.user) {
        return '/home'
    }
})

//export default router 