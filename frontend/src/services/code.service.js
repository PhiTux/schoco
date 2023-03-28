import axios from 'axios'
import { useAuthStore } from '../stores/auth.store.js';

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

    loadAllFiles(project_uuid, user_id) {
        return axiosAuth.get(`loadAllFiles/${project_uuid}/${user_id}`)
    }

    getProjectInfo(project_uuid, user_id) {
        return axiosAuth.get(`getProjectInfo/${project_uuid}/${user_id}`)
    }

    updateDescription(project_uuid, description) {
        return axiosAuth.post(`updateDescription/${project_uuid}`, { 'description': description })
    }

    saveFileChanges(changes, project_uuid, user_id) {
        return axiosAuth.post(`saveFileChanges/${project_uuid}/${user_id}`, { 'changes': changes })
    }

    getProjectsAsTeacher() {
        return axiosAuth.get('getProjectsAsTeacher')
    }

    getProjectsAsPupil() {
        return axiosAuth.get('getProjectsAsPupil')
    }

    prepareCompile(projectFiles, project_uuid, user_id) {
        return axiosAuth.post(`prepareCompile/${project_uuid}/${user_id}`, { 'files': projectFiles })
    }

    startCompile(ip, port, container_uuid, project_uuid, user_id) {
        return axiosAuth.post(`startCompile/${project_uuid}/${user_id}`, { 'ip': ip, 'port': port, 'container_uuid': container_uuid })
    }

    prepareExecute(project_uuid, user_id) {
        return axiosAuth.get(`prepareExecute/${project_uuid}/${user_id}`)
    }

    startExecute(ip, port, container_uuid, project_uuid, user_id) {
        return axiosAuth.post(`startExecute/${project_uuid}/${user_id}`, { 'ip': ip, 'port': port, 'container_uuid': container_uuid })
    }

    prepareTest(project_uuid, user_id) {
        return axiosAuth.get(`prepareTest/${project_uuid}/${user_id}`)
    }

    startTest(ip, port, container_uuid, project_uuid, user_id) {
        return axiosAuth.post(`startTest/${project_uuid}/${user_id}`, { 'ip': ip, 'port': port, 'container_uuid': container_uuid })
    }

    createHomework(orig_project_uuid, project_files, course_id, deadlineDate, computationTime) {
        return axiosAuth.post(`createHomework/${orig_project_uuid}`, { 'files': project_files, 'course_id': course_id, 'deadline_date': deadlineDate, 'computation_time': computationTime })
    }

    startHomework(id) {
        return axiosAuth.post('startHomework', {'id': id})
    }

    getHomeworkInfo(id) {
        return axiosAuth.post('getHomeworkInfo', {'id': id})
    }
}

export default new CodeService()