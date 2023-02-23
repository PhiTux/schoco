<script setup>
import { useAuthStore } from "../stores/auth.store.js";
import { useRoute } from "vue-router";

const authStore = useAuthStore();
const route = useRoute();

async function logout() {
  const authStore = useAuthStore();
  return authStore.logout();
}
</script>

<template>
  <nav class="navbar fixed-top navbar-dark navbar-expand-lg bg-dark">
    <div class="container-fluid">
      <a class="navbar-brand" href="/#/home">{🍫}</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item me-4">
            <a class="nav-link active" aria-current="page" href="/#/home">Home</a>
          </li>

          <a v-if="authStore.isTeacher() && route.name !== 'users'" class="btn btn-outline-secondary" href="/#/users">
            <font-awesome-icon icon="fa-solid fa-users" /> Benutzerverwaltung
          </a>
        </ul>
        <button v-if="authStore.user" class="btn btn-outline-secondary" type="submit" @click.prevent="logout()">
          Logout <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
        </button>
      </div>
    </div>
  </nav>
</template>

<style scoped></style>
