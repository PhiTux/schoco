<script setup>
import { reactive, onMounted, computed, ref } from "vue";
import UserService from "../services/user.service";

let allUsers = ref([]);

//let allUsers = reactive([]);

onMounted(() => {
  UserService.getAllUsers().then(
    (response) => {
      // remove unnecessary attribute 'hashed_password'
      allUsers.value = response.data.map(
        ({ hashed_password, ...keepAttrs }) => keepAttrs
      );
    },
    (error) => {
      console.log(error);
    }
  );
});

let allUsersFiltered = computed(() => {
  if (allUsers.value.length == 0) {
    return [];
  }
  return allUsers.value.filter((user) => true); // user.username === "teacher");
});

let allUsersFilteredSorted = computed(() => {
  if (!allUsersFiltered) {
    return [];
  }
  return allUsersFiltered.value;
});
</script>

<template>
  <h1>Users</h1>
  <div class="container">
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">#id</th>
          <th scope="col">Name</th>
          <th scope="col">Username</th>
          <th scope="col">Rolle</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="x in allUsersFilteredSorted">
          <th scope="row">{{ x.id }}</th>
          <td>{{ x.full_name }}</td>
          <td>{{ x.username }}</td>
          <td>{{ x.role }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped></style>
