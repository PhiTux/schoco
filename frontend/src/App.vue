<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="app d-flex flex-column">
    <NavBar />
    <router-view />
  </div>
</template>

<style scoped>
.app {
  /* width: 100vw; */
  /* height: 100vh; */
  background: #383838;
  color: rgb(240, 240, 240);
}
</style>
