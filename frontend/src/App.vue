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
:root {
  --green: #008e00;
  --green-hover: #007200;
  --green-disabled: #004700;
  --yellow: #ffd500;
  --yellow-hover: #ccaa00;
  --yellow-disabled: #806a00;
  --blue: #1b7cff;
  --blue-hover: #1662cc;
  --blue-disabled: #0e3d80;
  --indigo: #9003f7;
  --indigo-hover: #7302c6;
  --indigo-disabled: #48017b;
}

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
