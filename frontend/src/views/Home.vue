<script setup>
import { onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service";

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
    <h1>Meine Projekte</h1>
    justify-content-center
    <div class="d-flex align-content-start flex-wrap">
      <div class="card text-bg-dark m-2" v-for="p in state.myProjects">
        <div class="card-header">HA bis ... / eigenes Projekt</div>
        <div class="card-body">
          <h5 class="card-title">{{ p.name }}</h5>
          <p class="card-text">
            With supporting text below as a natural lead-in to additional
            content.
          </p>
          <a :href="'#/ide/' + p.uuid" class="btn btn-primary"
            >Projekt öffnen</a
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  width: 48%;
  transition: ease 0.3s;
}

.card:hover {
  box-shadow: 0 0 10px 3px #555;
}
</style>
