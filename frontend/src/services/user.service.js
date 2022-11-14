import axios from 'axios'
import { useAuthStore } from '../stores/auth.store';

const API_URL = import.meta.env.VITE_API_URL

const axiosAuth = axios.create({
    baseURL: API_URL
});
axiosAuth.interceptors.request.use((config) => {
    const authStore = useAuthStore()
    if (authStore.user) {
        const token = authStore.user.access_token
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}` 
        }
        return config
    }
}, (error) => {
    return Promise.reject(error)
})


class UserService {
    registerTeacher(teacherkey, first_name, last_name, username, password) {
        var bodyFormData = new FormData()
        bodyFormData.append("teacherkey", teacherkey);
        bodyFormData.append("first_name", first_name);
        bodyFormData.append("last_name", last_name);
        bodyFormData.append("username", username);
        bodyFormData.append("password", password);
        return axios.post(API_URL + 'registerTeacher', bodyFormData)
    }

    getAllUsers() {
        return axiosAuth.get('getAllUsers')
    }
}

export default new UserService()