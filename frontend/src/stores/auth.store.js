import { defineStore } from 'pinia'
import axios from 'axios'
//import { router } from '../router'

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
            var bodyFormData = new FormData()
            bodyFormData.append('username', username)
            bodyFormData.append('password', password)
            try {
                const response = await axios.post(API_URL + 'login', bodyFormData)
                if (response.data.access_token) {
                    this.user = response.data
                    localStorage.setItem('user', JSON.stringify(response.data))
                }
            } catch (err) {
                console.log(err)
            }
            this.$router.push(this.returnUrl || '/home');
        },
        logout() {
            this.user = null;
            localStorage.removeItem('user');
            this.$router.push('/login');
        }
    }
});