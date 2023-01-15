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
        return axiosAuth.post('createNewHelloWorld', { 'projectName': helloWorldName })
    }

    loadAllFiles(project_uuid) {
        return axiosAuth.post('loadAllFiles', { 'project_uuid': project_uuid })
    }

    getProjectName(project_uuid) {
        return axiosAuth.post('getProjectName', { 'project_uuid': project_uuid })
    }

    saveFileChanges(changes, project_uuid) {
        return axiosAuth.post('saveFileChanges', { 'changes': changes, 'project_uuid': project_uuid })
    }

    getMyProjects() {
        return axiosAuth.get('getMyProjects')
    }

    prepareCompile(projectFiles, project_uuid) {
        return axiosAuth.post('prepareCompile', {'files': projectFiles, 'project_uuid': project_uuid})
    }

    startCompile(ip, port, project_uuid) {
        return axiosAuth.post('startCompile', {'ip': ip, 'port': port, 'project_uuid': project_uuid})
    }
}

export default new CodeService()