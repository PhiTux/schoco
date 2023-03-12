<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue"
import { useAuthStore } from "../stores/auth.store.js";

const authStore = useAuthStore();

let state = reactive({
  myProjects: [],
  new_homework: [],
  editing_homework: [],
  old_homework: []
});


onBeforeMount(() => {
  CodeService.getMyProjects().then(
    (response) => {
      state.myProjects = response.data.projects;
      console.log(state.myProjects)
      //TODO create computed value where those projects are deleted, whichs are existing as homework
    },
    (error) => {
      console.log(error.response);
    }
  );
  CodeService.getHomework().then(
    (response) => {
      if (authStore.isTeacher()) {
        //TODO : separate homework to recent and old homework
        response.data.homework.forEach(e => {
          var project
          response.data.projects.forEach(p => {
            if (p.id == e.template_project_id) {
              project = p
            }
          })
          state.new_homework.push({ "name": project.name, "description": project.description, "deadline": e.deadline, "id": e.id })
        })

      } else {

        //state.homework = response.data;
        response.data.new.forEach(e => {
          var project
          response.data.projects.forEach(p => {
            if (p.id == e.template_project_id) {
              project = p
            }
          })
          //TODO: only put homework into this array, if the deadline is not yet passed - otherwise put it into old_homework
          state.new_homework.push({ "name": project.name, "description": project.description, "deadline": e.deadline, "uuid": project.uuid })
          console.log(new_homework)
        })
      }

      console.log(response.data)

    },
    (error) => {
      console.log(error.response)
    }
  )
});
</script>

<template>
  <div class="container">
    <a class="btn btn-outline-success my-3" type="submit" href="/#/newProject">
      Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
    </a>
    <h1>Aktuelle Hausaufgaben</h1>
    <!-- if teacher: -->
    <ProjectCard v-if="authStore.isTeacher()" v-for="h in state.new_homework" isHomework isNew isTeacher :name="h.name"
      :description="h.description" :id="h.id" :deadline="h.deadline" />

    <!-- new homework -->
    <ProjectCard v-else v-for="h in state.new_homework" isHomework isNew :name="h.name" :description="h.description"
      :uuid="h.uuid" :deadline="h.deadline" />
    <ProjectCard v-else v-for="h in state.new_homework" isHomework isNew :name="h.name" :description="h.description"
      :uuid="h.uuid" :deadline="h.deadline" />
    <!-- homework, which i'm working on -->
    <ProjectCard v-for="p in state.editing_homework" :name="p.name" :description="p.description" :uuid="p.uuid" />

    <h1>Frühere Hausaufgaben</h1>

    <h1>Meine Projekte</h1>
    <div class="d-flex align-content-start flex-wrap">
      <ProjectCard v-for="p in state.myProjects" :name="p.name" :description="p.description" :uuid="p.uuid" />
      <!-- <div class="card text-bg-dark m-2" v-for="p in state.myProjects">
                                                                                <div class="card-header">HA bis ... / eigenes Projekt</div>
                                                                                <div class="card-body">
                                                                                  <h5 class="card-title">{{ p.name }}</h5>
                                                                                  <p class="card-text">
                                                                                    {{ p.description }}
                                                                                  </p>
                                                                                  <a :href="'#/ide/' + p.uuid" class="btn btn-primary">Projekt öffnen</a>
                                                                                </div>
                                                                            </div> -->
    </div>
  </div>
</template>

<style scoped>
.card-text {
  white-space: pre-line;
}
</style>
