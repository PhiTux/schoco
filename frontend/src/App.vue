<script setup>
import NavBar from "./components/NavBar.vue";
import { useRoute } from "vue-router";
const route = useRoute();
</script>

<template>
  <div class="app d-flex flex-column">
    <NavBar v-if="route.name !== 'ide'" />
    <div :class="{ main: route.name !== 'ide' }">
      <router-view />
    </div>
  </div>
</template>

<style>
body {
  background-color: #383838 !important;
}
</style>

<style scoped>
.app {
  /* width: 100vw;*/
  /*height: 100%;*/
  /*background: #383838;*/
  color: rgb(240, 240, 240);
}

.main {
  padding-top: 56px;
  /* height: 100%; */
}
</style>
