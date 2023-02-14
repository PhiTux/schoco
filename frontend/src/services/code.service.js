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
    createNewHelloWorld(helloWorldName, helloWorldDescription) {
        return axiosAuth.post('createNewHelloWorld', { 'projectName': helloWorldName, 'projectDescription': helloWorldDescription })
    }

    loadAllFiles(project_uuid) {
        return axiosAuth.get(`loadAllFiles/${project_uuid}`)
    }

    getProjectInfo(project_uuid) {
        return axiosAuth.get(`getProjectInfo/${project_uuid}`)
    }

    updateDescription(project_uuid, description) {
        return axiosAuth.post(`updateDescription/${project_uuid}`, {'description': description})
    }

    saveFileChanges(changes, project_uuid) {
        return axiosAuth.post(`saveFileChanges/${project_uuid}`, { 'changes': changes})
    }

    getMyProjects() {
        return axiosAuth.get('getMyProjects')
    }

    prepareCompile(projectFiles, project_uuid) {
        return axiosAuth.post(`prepareCompile/${project_uuid}`, {'files': projectFiles})
    }

    startCompile(ip, port, container_uuid, project_uuid) {
        return axiosAuth.post(`startCompile/${project_uuid}`, {'ip': ip, 'port': port, 'container_uuid': container_uuid})
    }

    prepareExecute(project_uuid) {
        return axiosAuth.get(`prepareExecute/${project_uuid}`)
    }

    startExecute(ip, port, container_uuid, project_uuid) {
        return axiosAuth.post(`startExecute/${project_uuid}`, {'ip': ip, 'port': port, 'container_uuid': container_uuid})
    }

    prepareTest(project_uuid) {
        return axiosAuth.get(`prepareTest/${project_uuid}`)
    }

    startTest(ip, port, container_uuid, project_uuid) {
        return axiosAuth.post(`startTest/${project_uuid}`, {'ip': ip, 'port': port, 'container_uuid': container_uuid})
    }
}

export default new CodeService()