<script setup>
import { reactive, computed } from "vue";
import { useAuthStore } from "../stores/auth.store";

const state = reactive({
  username: "",
  password: "",
  showPassword: false,
});

async function login() {
  const authStore = useAuthStore();
  return authStore.login(state.username, state.password);
}

function showPassword() {
  state.showPassword = true;
}

function hidePassword() {
  state.showPassword = false;
}

let loginValid = computed(() => {
  return state.username != "" && state.password != "";
});
</script>

<template>
  <div
    class="container-fluid flex-fill align-items-center d-flex justify-content-center"
  >
    <div class="w-100 row text-center align-items-center">
      <div class="col-6">
        <div class="container-lg">
          {🍫}<br />SCHOCO<br />
          SCHool Online COding
        </div>
      </div>
      <div class="col-6 col-xxl-4">
        <div class="accordion" id="loginAccordion">
          <div class="accordion-item">
            <h2 class="accordion-header" id="headingOne">
              <button
                class="accordion-button"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#collapseOne"
                aria-expanded="true"
                aria-controls="collapseOne"
              >
                Login
              </button>
            </h2>
            <div
              id="collapseOne"
              class="accordion-collapse collapse show"
              aria-labelledby="headingOne"
              data-bs-parent="#loginAccordion"
            >
              <div class="accordion-body">
                <form @submit.prevent="login">
                  <div class="input-group mb-3">
                    <span class="input-group-text" id="basic-addon1">
                      <font-awesome-icon icon="fa-solid fa-user"
                    /></span>
                    <div class="form-floating">
                      <input
                        type="text"
                        id="floatingInput"
                        class="form-control"
                        v-model="state.username"
                        placeholder="Username"
                      />
                      <label for="floatingInput">Username</label>
                    </div>
                  </div>

                  <div class="input-group mb-3">
                    <span class="input-group-text" id="basic-addon1"
                      ><font-awesome-icon icon="fa-solid fa-key"
                    /></span>
                    <div class="form-floating">
                      <input
                        :type="[state.showPassword ? 'text' : 'password']"
                        id="floatingPassword"
                        class="form-control"
                        v-model="state.password"
                        placeholder="Password"
                      />
                      <label for="floatingPassword">Password</label>
                    </div>
                    <span class="input-group-text" id="basic-addon1">
                      <a
                        class="greyButton"
                        @mousedown="showPassword()"
                        @mouseup="hidePassword()"
                        @mouseleave="hidePassword()"
                        ><font-awesome-icon
                          v-if="!state.showPassword"
                          icon="fa-solid fa-eye-slash" /><font-awesome-icon
                          v-else
                          icon="fa-solid fa-eye" /></a
                    ></span>
                  </div>
                  <button
                    class="btn btn-primary"
                    :class="{ disabled: !loginValid }"
                  >
                    Login
                  </button>
                </form>
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header" id="headingTwo">
              <button
                class="accordion-button collapsed"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#collapseTwo"
                aria-expanded="false"
                aria-controls="collapseTwo"
              >
                Registrierung nur für Lehrkräfte
              </button>
            </h2>
            <div
              id="collapseTwo"
              class="accordion-collapse collapse"
              aria-labelledby="headingTwo"
              data-bs-parent="#loginAccordion"
            >
              <div class="accordion-body">
                <strong>This is the second item's accordion body.</strong> It is
                hidden by default, until the collapse plugin adds the
                appropriate classes that we use to style each element. These
                classes control the overall appearance, as well as the showing
                and hiding via CSS transitions. You can modify any of this with
                custom CSS or overriding our default variables. It's also worth
                noting that just about any HTML can go within the
                <code>.accordion-body</code>, though the transition does limit
                overflow.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.greyButton {
  text-decoration: none;
  color: inherit;
}
</style>
