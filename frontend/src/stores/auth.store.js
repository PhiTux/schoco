import { defineStore } from 'pinia'
import axios from 'axios'

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
                return err
            }
            
            if (this.user.must_change_password) {
                this.$router.push('/changePassword');
            } else {
                this.$router.push(this.returnUrl || '/home');
            }
            return
        },
        logout() {
            this.user = null;
            this.$router.push('/login');
            localStorage.removeItem('user');
        },
        logout_username_changed() {
            this.user = null;
            localStorage.removeItem('user');
            this.$router.push({ path: '/login', query: { username_changed: true } });
        },
        logout_token_expired() {
            this.user = null;
            localStorage.removeItem('user');
            this.$router.push({ path: '/login', query: { token_expired: true } });
        },
        isTeacher() {
            return (this.user && this.user.role == 'teacher')
        },
        setPasswordChanged() {
            this.user.must_change_password = false
            localStorage.setItem('user', JSON.stringify(this.user))
        }
    }
});