<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="app d-flex flex-column">
    <NavBar />
    <div class="main">
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
