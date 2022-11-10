import {createRouter, createWebHashHistory} from 'vue-router'
import { useAuthStore } from '../stores/auth.store.js'
import Login from "../views/Login.vue";
import Home from "../views/Home.vue";

const routes = [
    {path: '/login', component: Login},
    {path: '/home', component: Home},
]

export const router = createRouter({
    history: createWebHashHistory(),
    routes
})

router.beforeEach(async (to) => {
    const publicPages = ['/login']
    const authRequired = !publicPages.includes(to.path)
    const auth = useAuthStore()

    if (authRequired && !auth.user) {
        auth.returnUrl = to.fullPath;
        return '/login'
    }
})

//export default router 