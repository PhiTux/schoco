<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue"
import { useAuthStore } from "../stores/auth.store.js";

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
</script>

<template>
  <div class="container">
    <a class="btn btn-outline-success my-3" type="submit" href="/#/newProject">
      Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
    </a>
    <h1>Aktuelle Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <!-- if teacher: -->
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.new_homework" isHomework isNew isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" />

      <!-- else -->
      <ProjectCard v-else v-for="h in state.new_homework" isHomework isNew :isEditing="h.is_editing" :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" />
    </div>

    <h1>Frühere Hausaufgaben</h1>
    <div class="d-flex align-content-start flex-wrap">
      <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.old_homework" isHomework isOld isTeacher :name="h.name"
        :description="h.description" :id="h.id" :deadline="h.deadline" :courseName="h.course_name"
        :courseColor="h.course_color" :courseFontDark="h.course_font_dark" />

      <ProjectCard v-else v-for="h in state.old_homework" isHomework isOld :name="h.name" :description="h.description"
        :id="h.id" :deadline="h.deadline" :courseName="h.course_name" :courseColor="h.course_color"
        :courseFontDark="h.course_font_dark" />
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
