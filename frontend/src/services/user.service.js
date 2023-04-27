import axios from 'axios'
import { useAuthStore } from '../stores/auth.store.js';
import jwt_decode from 'jwt-decode'

const API_URL = import.meta.env.VITE_API_URL

const axiosAuth = axios.create({
    baseURL: API_URL
});
axiosAuth.interceptors.request.use((config) => {    
    const authStore = useAuthStore()
    if (authStore.user) {
        // go to login if token has expired
        let decoded = jwt_decode(authStore.user.access_token)
        if (decoded.exp < Date.now() / 1000) {
            authStore.logout_token_expired()
            return Promise.reject('Token expired')
        }

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
    registerTeacher(teacherkey, name, username, password) {
        var bodyFormData = new FormData()
        bodyFormData.append("teacherkey", teacherkey);
        bodyFormData.append("full_name", name);
        bodyFormData.append("username", username);
        bodyFormData.append("password", password);
        return axios.post(API_URL + 'registerTeacher', bodyFormData)
    }

    registerPupils(newPupils) {
        return axiosAuth.post('registerPupils', { 'newPupils': newPupils })
    }

    setNewPassword(username, password) {
        return axiosAuth.post('setNewPassword', { 'username': username, 'password': password })
    }

    getAllUsers() {
        return axiosAuth.get('getAllUsers')
    }

    getAllCourses() {
        return axiosAuth.get('getAllCourses')
    }

    addNewCourse(courseName, courseColor, courseFontDark) {
        return axiosAuth.post('addNewCourse', { 'name': courseName, 'color': courseColor, 'fontDark': courseFontDark })
    }

    removeCourse(course_id) {
        return axiosAuth.post('removeCourse', { 'id': course_id })
    }

    addCourseToUser(user_id, coursename) {
        return axiosAuth.post('addCourseToUser', { 'user_id': user_id, 'coursename': coursename })
    }

    removeCourseFromUser(user_id, course_id) {
        return axiosAuth.post('removeCourseFromUser', { 'user_id': user_id, 'course_id': course_id })
    }

    deleteUser(user_id) {
        return axiosAuth.post('deleteUser', { 'user_id': user_id })
    }

    changeName(user_id, name) {
        return axiosAuth.post('changeName', {'user_id': user_id, 'name': name})
    }

    changeUsername(user_id, username) {
        return axiosAuth.post('changeUsername', {'user_id': user_id, 'name': username})
    }
}

export default new UserService()