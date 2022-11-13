import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

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
}

export default new UserService()