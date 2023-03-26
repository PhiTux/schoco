<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue"
import { useAuthStore } from "../stores/auth.store.js";
import { useRouter } from "vue-router";
import { Toast } from "bootstrap";


const router = useRouter()

const authStore = useAuthStore();

let state = reactive({
  myProjects: [],
  new_homework: [],
  old_homework: []
});


onBeforeMount(() => {

  if (authStore.isTeacher()) {
    CodeService.getProjectsAsTeacher().then(
      (response) => {
        console.log(response.data)
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
        console.log(error.response)
      }
    )
  } else {
    CodeService.getProjectsAsPupil().then(
      (response) => {
        console.log(response.data)
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
        console.log(error.response)
      }
    )
  }
});

function startHomework(id) {
  console.log("startHomework", id)
  CodeService.startHomework(id).then(
    (response) => {
      console.log(response.data)
      if (response.data.success) {
        router.push({
          name: "ide",
          params: { project_uuid: response.data.uuid },
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
  </div>

  <div class="container">
    <a class="btn btn-outline-success my-3" type="submit" href="/#/newProject">
      Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
    </a>
    <h1>Aktuelle Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <!-- if teacher: -->
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.new_homework" isHomework isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" />

      <!-- else -->
      <ProjectCard v-else v-for="h in state.new_homework" isHomework @startHomework="startHomework"
        :isEditing="h.is_editing" :name="h.name" :description="h.description" :uuid="h.uuid" :id="h.id"
        :deadline="h.deadline" />
    </div>

    <h1>Frühere Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <!-- if teacher: -->
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.old_homework" isHomework isOld isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" />

      <!-- else -->
      <ProjectCard v-else v-for="h in state.old_homework" isHomework isOld @startHomework="startHomework"
        :isEditing="h.is_editing" :name="h.name" :uuid="h.uuid" :description="h.description" :id="h.id"
        :deadline="h.deadline" />
    </div>

    <h1>Meine Projekte</h1>
    <div class="d-flex align-content-start flex-wrap">
      <ProjectCard v-for="p in state.myProjects" :name="p.name" :description="p.description" :uuid="p.uuid" />
    </div>
  </div>
</template>

<style scoped>
.card-text {
  white-space: pre-line;
}
</style>
