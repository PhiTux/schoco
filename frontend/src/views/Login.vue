<script setup>
import { reactive, computed } from "vue";
import { useAuthStore } from "../stores/auth.store";

const state = reactive({
  username: "",
  password: "",
});

async function login() {
  const authStore = useAuthStore();
  return authStore
    .login(state.username, state.password)
    .then((r) => console.log(r))
    .catch((e) => console.log(e));
}

let loginValid = computed(() => {
  return state.username != "" && state.password != "";
});
</script>

<template>
  <h1>Login</h1>
  <div class="text-center">
    <div class="container w-100 m-auto">
      <div class="row">
        <div class="col">
          {🍫}<br />SCHOCO<br />
          SCHool Online COding
        </div>
        <div class="col">
          <form @submit.prevent="login">
            <div class="form-floating">
              <input
                type="text"
                id="floatingInput"
                class="form-control"
                v-model="state.username"
              />
              <label for="floatingInput">Username</label>
            </div>
            <div class="form-floating">
              <input
                type="password"
                id="floatingPassword"
                class="form-control"
                v-model="state.password"
              />
              <label for="floatingPassword">Password</label>
            </div>
            <button class="btn btn-primary" :class="{ disabled: !loginValid }">
              Huhuh
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
