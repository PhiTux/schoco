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

class CodeService {
    createNewHelloWorld(helloWorldName) {
        return axiosAuth.post('createNewHelloWorld', {'projectName': helloWorldName})
    }

    loadAllFiles(project_uuid) {
        return axiosAuth.post('loadAllFiles', {'project_uuid': project_uuid})
    }
}

export default new CodeService()