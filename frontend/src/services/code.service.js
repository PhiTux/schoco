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

class CodeService {
    createNewHelloWorld(helloWorldName, className, helloWorldDescription, language) {
        return axiosAuth.post('createNewHelloWorld', { 'projectName': helloWorldName, 'className': className, 'projectDescription': helloWorldDescription, 'language': language })
    }

    loadAllFiles(project_uuid, user_id) {
        return axiosAuth.get(`loadAllFiles/${project_uuid}/${user_id}`)
    }

    getProjectInfo(project_uuid, user_id) {
        return axiosAuth.get(`getProjectInfo/${project_uuid}/${user_id}`)
    }

    updateDescription(project_uuid, user_id, description) {
        return axiosAuth.post(`updateDescription/${project_uuid}/${user_id}`, { 'text': description })
    }

    updateProjectName(project_uuid, user_id, projectName) {
        return axiosAuth.post(`updateProjectName/${project_uuid}/${user_id}`, { 'text': projectName })
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

    startCompile(projectFiles, project_uuid, user_id) {
        return axiosAuth.post(`startCompile/${project_uuid}/${user_id}`, { 'files': projectFiles })
    }

    prepareExecute(project_uuid, user_id) {
        return axiosAuth.get(`prepareExecute/${project_uuid}/${user_id}`)
    }

    startExecute(ip, port, container_uuid, project_uuid, user_id, save_output) {
        return axiosAuth.post(`startExecute/${project_uuid}/${user_id}`, { 'ip': ip, 'port': port, 'container_uuid': container_uuid, 'save_output': save_output })
    }

    prepareTest(project_uuid, user_id) {
        return axiosAuth.get(`prepareTest/${project_uuid}/${user_id}`)
    }

    startTest(ip, port, container_uuid, project_uuid, user_id) {
        return axiosAuth.post(`startTest/${project_uuid}/${user_id}`, { 'ip': ip, 'port': port, 'container_uuid': container_uuid })
    }

    createHomework(orig_project_uuid, project_files, course_id, deadlineDate, computationTime, enableTests) {
        return axiosAuth.post(`createHomework/${orig_project_uuid}`, { 'files': project_files, 'course_id': course_id, 'deadline_date': deadlineDate, 'computation_time': computationTime, 'enable_tests': enableTests })
    }

    startHomework(id) {
        return axiosAuth.post('startHomework', { 'id': id })
    }

    getHomeworkInfo(id) {
        return axiosAuth.post('getHomeworkInfo', { 'id': id })
    }

    deleteProject(uuid, user_id) {
        return axiosAuth.post(`deleteProject/${uuid}`, { 'user_id': user_id })
    }

    deleteHomework(id) {
        return axiosAuth.post('deleteHomework', { 'id': id })
    }

    renameFile(project_uuid, user_id, oldName, newName, fileContent, sha) {
        return axiosAuth.post(`renameFile/${project_uuid}/${user_id}`, { 'old_path': oldName, 'new_path': newName, 'content': fileContent, 'sha': sha })
    }

    renameHomework(id, newName) {
        return axiosAuth.post('renameHomework', { 'id': id, 'new_name': newName })
    }

    renameProject(uuid, new_name) {
        return axiosAuth.post(`renameProject/${uuid}`, { 'text': new_name })
    }

    duplicateProject(uuid) {
        return axiosAuth.post(`duplicateProject/${uuid}`)
    }

    downloadProject(uuid) {
        return axiosAuth.get(`downloadProject/${uuid}`, { responseType: 'blob' })
    }

    uploadProject(file, config) {
        const formData = new FormData();
        formData.append('file', file);
        return axiosAuth.postForm('uploadProject', file, config)
    }

    addNewClass(project_uuid, user_id, className, language) {
        return axiosAuth.post(`addNewClass/${project_uuid}/${user_id}`, { 'className': className, 'language': language })
    }

    deleteFile(project_uuid, user_id, path, sha) {
        return axiosAuth.post(`deleteFile/${project_uuid}/${user_id}`, { 'path': path, 'sha': sha })
    }

    updateHomeworkSettings(id, deadlineDate, computationTime, enableTests) {
        return axiosAuth.post('updateHomeworkSettings', { 'id': id, 'deadline_date': deadlineDate, 'computation_time': computationTime, 'enable_tests': enableTests })
    }

    stopContainer(uuid) {
        return axiosAuth.post('stopContainer', {'uuid': uuid})
    }

    addSolution(homework_id, solution_id, solution_start_showing) {
        return axiosAuth.post('addSolution', {'homework_id': homework_id, 'solution_id': solution_id, 'solution_start_showing': solution_start_showing})
    }

    deleteSolution(homework_id) {
        return axiosAuth.post('deleteSolution', {'homework_id': homework_id})
    }

    loadEntryPoint(project_uuid, user_id) {
        return axiosAuth.get(`loadEntryPoint/${project_uuid}/${user_id}`)
    }

    setEntryPoint(project_uuid, user_id, path) {
        return axiosAuth.post(`setEntryPoint/${project_uuid}/${user_id}`, {'entry_point': path})
    }

    getTeacherComputationTime(project_uuid, user_id) {
        return axiosAuth.get(`getTeacherComputationTime/${project_uuid}/${user_id}`)
    }

    setTeacherComputationTime(computation_time, project_uuid, user_id) {
        return axiosAuth.post(`setTeacherComputationTime/${project_uuid}/${user_id}`, {'computation_time': computation_time})
    }
}

export default new CodeService()