<script setup>
import { onMounted } from "vue";
import UserService from "../services/user.service";

onMounted(() => {
  UserService.getAllUsers().then(
    (response) => {
      console.log(response);
    },
    (error) => {
      console.log(error);
    }
  );
});
</script>

<template>
  <h1>Users</h1>
</template>

<style scoped></style>
