import { defineStore } from 'pinia'
import axios from 'axios'
import { router } from '../router'

//const baseUrl = `${import.meta.env.VITE_API_URL}/users`;
const API_URL = import.meta.env.VITE_API_URL

export const useAuthStore = defineStore({
    id: 'auth',
    state: () => ({
        // initialize state from local storage to enable user to stay logged in
        user: JSON.parse(localStorage.getItem('user')),
        returnUrl: null
    }),
    actions: {
        async login(username, password) {
            axios.post(API_URL + 'login', {
                username: username,
                password: password
            })
            .then(response => {
                if (response.data.token) {
                    // update pinia state
                    this.user = response.data;
                    
                    localStorage.setItem('user', JSON.stringify(response.data))
                }
                router.push(this.returnUrl || '/home');
            })

        },
        logout() {
            this.user = null;
            localStorage.removeItem('user');
            router.push('/login');
        }
    }
});