<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue"

let state = reactive({
  myProjects: [],
});

onBeforeMount(() => {
  CodeService.getMyProjects().then(
    (response) => {
      state.myProjects = response.data.projects;
    },
    (error) => {
      console.log(error);
    }
  );
});
</script>

<template>
  <div class="container">
    <a class="btn btn-outline-success my-3" type="submit" href="/#/newProject">
      Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
    </a>
    <h1>Aktuelle Hausaufgaben</h1>

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
