<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue"
import { useAuthStore } from "../stores/auth.store.js";
import { useRouter } from "vue-router";
import { Toast, Modal } from "bootstrap";


const router = useRouter()

const authStore = useAuthStore();

let state = reactive({
  myProjects: [],
  new_homework: [],
  old_homework: [],
  projectToDelete: null,
});

onBeforeMount(() => {
  if (authStore.isTeacher()) {
    getProjectsAsTeacher()
  } else {
    getProjectsAsPupil()
  }
});

function getProjectsAsTeacher() {
  CodeService.getProjectsAsTeacher().then(
    (response) => {
      state.myProjects = response.data.projects
      response.data.homework.forEach(h => {
        if (new Date(h.deadline) > new Date()) {
          state.new_homework.push(h)
        } else {
          state.old_homework.push(h)
        }
      })
    },
    (error) => {
      if (error.response) {
        console.log(error.response)
      }
    }
  )
}

function getProjectsAsPupil() {
  CodeService.getProjectsAsPupil().then(
    (response) => {
      state.myProjects = response.data.projects
      state.new_homework = []
      state.old_homework = []

      response.data.homework.forEach(h => {
        if (new Date(h.deadline) > new Date()) {
          state.new_homework.push(h)
        } else {
          state.old_homework.push(h)
        }
      })
    },
    (error) => {
      if (error.response) {
        console.log(error.response)
      }

    }
  )
}

function startHomework(id) {
  console.log("startHomework", id)
  CodeService.startHomework(id).then(
    (response) => {
      if (response.data.success) {
        router.push({
          name: "ide",
          params: { project_uuid: response.data.uuid, user_id: response.data.branch },
        });
      }
    },
    error => {
      console.log(error.response)
      const toast = new Toast(
        document.getElementById("toastStartHomeworkError")
      );
      toast.show();
    }
  )
}

function askDeleteHomework(id, name) {
  state.deleteId = id
  state.deleteName = name
  const modal = new Modal(document.getElementById("deleteHomeworkModal"))
  modal.show()
}

function askDeleteProject(uuid, user_id, name) {
  state.deleteUuid = uuid
  state.deleteUserId = user_id
  state.deleteName = name
  if (user_id === undefined) {
    const modal = new Modal(document.getElementById("deleteProjectModal"))
    modal.show()
  } else {
    const modal = new Modal(document.getElementById("deleteHomeworkBranchModal"))
    modal.show()
  }
}

function deleteProject(uuid, user_id) {
  if (user_id === undefined)
    user_id = 0

  //show modal which asks if the user really wants to delete the project


  CodeService.deleteProject(uuid, user_id).then(
    (response) => {
      if (response.data) {
        state.myProjects = state.myProjects.filter(p => p.uuid != uuid)
        if (user_id != 0) {
          getProjectsAsPupil()
        }

        const toast = new Toast(
          document.getElementById("toastDeleteProjectSuccess")
        );
        toast.show();

      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteProjectError")
        );
        toast.show();
      }
    },
    error => {
      console.log(error.response)
    }
  )
}

function deleteHomework(id) {
  CodeService.deleteHomework(id).then(
    (response) => {
      if (response.data) {
        state.new_homework = state.new_homework.filter(p => p.id != id)
        state.old_homework = state.old_homework.filter(p => p.id != id)

        const toast = new Toast(
          document.getElementById("toastDeleteProjectSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteProjectError")
        );
        toast.show();
      }
    },
    error => {
      console.log(error.response)
    }
  )
}

</script>

<template>
  <!-- Toasts -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div class="toast align-items-center text-bg-danger border-0" id="toastStartHomeworkError" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Fehler beim Starten der Hausaufgabe. Probiere es erneut und frage andernfalls deine Lehrkraft um Hilfe.
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteProjectError" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Fehler beim Löschen des Projekts / der Hausaufgabe.
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-success border-0" id="toastDeleteProjectSuccess" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Das Projekt oder die Hausaufgabe wurde erfolgreich gelöscht.
        </div>
      </div>
    </div>
  </div>

  <!-- Modals -->
  <div class="modal fade" id="deleteProjectModal" tabindex="-1" aria-labelledby="deleteProjectModalLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">Privates Projekt löschen?</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Möchtest du wirklich dein eigenes, privates Projekt mit dem Titel <b>{{ state.deleteName }}</b>
          löschen?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
          <button @click.prevent="deleteProject(state.deleteUuid, state.deleteUserId)" type="button"
            class="btn btn-primary" data-bs-dismiss="modal">Löschen</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="deleteHomeworkBranchModal" tabindex="-1" aria-labelledby="deleteHomeworkBranchModalLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">Fortschritt löschen?</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Du kannst eine Hausaufgabe nicht völlig löschen. Du kannst nur deinen bisherigen Fortschritt löschen und
          anschließend wieder in einem "sauberen" Projekt von vorne beginnen.
          <br>
          <br>
          Möchtest du wirklich deinen Fortschritt
          von <b>{{ state.deleteName }}</b>
          löschen?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
          <button @click.prevent="deleteProject(state.deleteUuid, state.deleteUserId)" type="button"
            class="btn btn-primary" data-bs-dismiss="modal">Löschen</button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="deleteHomeworkModal" tabindex="-1" aria-labelledby="deleteHomeworkModalLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">Hausaufgabe löschen?</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Wenn du eine Hausaufgabe löschst, dann wird sie auch bei allen Schüler/innen gelöscht. Möchtest du wirklich die
          Hausaufgabe mit dem Titel <b>{{ state.deleteName }}</b> löschen?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
          <button @click.prevent="deleteHomework(state.deleteId)" type="button" class="btn btn-primary"
            data-bs-dismiss="modal">Löschen</button>
        </div>
      </div>
    </div>
  </div>


  <div class="container">
    <a class="btn btn-outline-success my-3" type="submit" href="/#/newProject">
      Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
    </a>
    <h1 v-if="state.new_homework.length">Aktuelle Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <!-- if teacher: -->
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.new_homework" isHomework isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" @deleteHomework="askDeleteHomework" />

      <!-- else -->
      <ProjectCard v-else v-for="h in state.new_homework" isHomework @startHomework="startHomework"
        :isEditing="h.is_editing" :name="h.name" :description="h.description" :uuid="h.uuid" :branch="h.branch" :id="h.id"
        :deadline="h.deadline" @deleteProject="askDeleteProject" />
    </div>

    <h1 v-if="state.old_homework.length">Frühere Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <!-- if teacher: -->
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.old_homework" isHomework isOld isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" @deleteHomework="askDeleteHomework" />

      <!-- else -->
      <ProjectCard v-else v-for="h in state.old_homework" isHomework isOld @startHomework="startHomework"
        :isEditing="h.is_editing" :name="h.name" :uuid="h.uuid" :description="h.description" :branch="h.branch" :id="h.id"
        :deadline="h.deadline" @deleteProject="askDeleteProject" />
    </div>

    <h1 v-if="state.myProjects.length">Meine Projekte</h1>
    <div class="d-flex align-content-start flex-wrap">
      <ProjectCard v-for="p in state.myProjects" :name="p.name" :description="p.description" :uuid="p.uuid"
        @deleteProject="askDeleteProject" />
    </div>
  </div>
</template>

<style scoped>
.dark-text {
  color: var(--bs-dark);
}

.card-text {
  white-space: pre-line;
}
</style>
