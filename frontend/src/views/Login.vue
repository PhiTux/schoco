<script setup>
import { reactive, computed } from "vue";
import { useAuthStore } from "../stores/auth.store";
import UserService from "../services/user.service";

const state = reactive({
  loginUsername: "",
  loginPassword: "",
  registerTeacherKey: "",
  registerName: "",
  registerUsername: "",
  registerPassword1: "",
  registerPassword2: "",
  showLoginPassword: false,
  showRegisterPassword1: false,
  showRegisterPassword2: false,
  loginIncomplete: false,
  registerIncomplete: false,
  showLoginError: false,
  showRegistrationSuccess: false,
});

async function login() {
  if (!this.loginValid) {
    state.loginIncomplete = true;
    return;
  }
  const authStore = useAuthStore();
  const result = await authStore.login(
    state.loginUsername,
    state.loginPassword
  );
  if (result && result.response.status == 401) {
    state.loginIncomplete = false;
    state.showLoginError = true;
  }
}

async function registerTeacher() {
  if (
    !this.registerValid ||
    !this.registerPasswordsEqual ||
    this.registerPasswordTooShort
  ) {
    state.registerIncomplete = true;
    return;
  }
  UserService.registerTeacher(
    state.registerTeacherKey,
    state.registerName,
    state.registerUsername,
    state.registerPassword1
  ).then(
    (response) => {
      state.showRegistrationSuccess = true;
      state.showRegistrationError = false;
    },
    (error) => {
      state.showRegistrationError = true;
      state.showRegistrationSuccess = false;
    }
  );
}

function showLoginPassword() {
  state.showLoginPassword = true;
}

function showRegisterPassword1() {
  state.showRegisterPassword1 = true;
}

function showRegisterPassword2() {
  state.showRegisterPassword2 = true;
}

function hideLoginPassword() {
  state.showLoginPassword = false;
}

function hideRegisterPassword1() {
  state.showRegisterPassword1 = false;
}

function hideRegisterPassword2() {
  state.showRegisterPassword2 = false;
}

let registerValid = computed(() => {
  let tmp =
    state.registerTeacherKey != "" &&
    state.registerName != "" &&
    state.registerUsername != "" &&
    state.registerPassword1 != "" &&
    state.registerPassword2 != "";
  if (tmp) state.registerIncomplete = false;
  return tmp;
});

let loginValid = computed(() => {
  var tmp = state.loginUsername != "" && state.loginPassword != "";
  if (tmp) state.loginIncomplete = false;
  return tmp;
});

let registerPasswordsEqual = computed(() => {
  return state.registerPassword1 === state.registerPassword2;
});

let registerPasswordTooShort = computed(() => {
  return (
    state.registerPassword1.length > 0 && state.registerPassword1.length < 8
  );
});
</script>

<template>
  <div class="center-fix d-flex flex-column">
    <div
      class="container-fluid flex-fill align-items-center d-flex justify-content-center"
    >
      <div class="w-100 row text-center align-items-center">
        <div class="col-6">
          <div class="container-lg">
            {????}<br />SCHOCO<br />
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
                  <form @submit.prevent="login()">
                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1">
                        <font-awesome-icon icon="fa-solid fa-user"
                      /></span>
                      <div class="form-floating">
                        <input
                          type="text"
                          id="floatingInputLogin"
                          class="form-control"
                          v-model="state.loginUsername"
                          placeholder="Username"
                        />
                        <label for="floatingInputLogin">Username</label>
                      </div>
                    </div>

                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1"
                        ><font-awesome-icon icon="fa-solid fa-key"
                      /></span>
                      <div class="form-floating">
                        <input
                          :type="[
                            state.showLoginPassword ? 'text' : 'password',
                          ]"
                          id="floatingPasswordLogin"
                          class="form-control"
                          v-model="state.loginPassword"
                          placeholder="Password"
                        />
                        <label for="floatingPasswordLogin">Password</label>
                      </div>
                      <span class="input-group-text" id="basic-addon1">
                        <a
                          class="greyButton"
                          @mousedown="showLoginPassword()"
                          @mouseup="hideLoginPassword()"
                          @mouseleave="hideLoginPassword()"
                          ><font-awesome-icon
                            v-if="!state.showLoginPassword"
                            icon="fa-solid fa-eye-slash" /><font-awesome-icon
                            v-else
                            icon="fa-solid fa-eye" /></a
                      ></span>
                    </div>
                    <div
                      v-if="state.loginIncomplete"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Eingabe unvollst??ndig
                    </div>
                    <div
                      v-if="state.showLoginError"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Falscher Benutzername oder Passwort
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
                  Registrierung nur f??r Lehrkr??fte
                </button>
              </h2>
              <div
                id="collapseTwo"
                class="accordion-collapse collapse"
                aria-labelledby="headingTwo"
                data-bs-parent="#loginAccordion"
              >
                <div class="accordion-body">
                  <form @submit.prevent="registerTeacher()">
                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1">
                        <font-awesome-icon icon="fa-solid fa-lock"
                      /></span>
                      <div class="form-floating">
                        <input
                          type="password"
                          id="floatingInputTeacherKey"
                          class="form-control"
                          v-model="state.registerTeacherKey"
                          placeholder="Lehrer-Passwort"
                        />
                        <label for="floatingInputTeacherKey"
                          >Lehrer-Passwort</label
                        >
                      </div>
                    </div>

                    <hr />

                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1">
                        <font-awesome-icon icon="fa-solid fa-signature"
                      /></span>
                      <div class="form-floating">
                        <input
                          :disabled="state.registerTeacherKey == ''"
                          type="text"
                          id="floatingInputRegisterName"
                          class="form-control"
                          v-model="state.registerName"
                          placeholder="Vor- und Nachname"
                        />
                        <label for="floatingInputRegisterName"
                          >Vor- und Nachname</label
                        >
                      </div>
                    </div>

                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1">
                        <font-awesome-icon icon="fa-solid fa-user"
                      /></span>
                      <div class="form-floating">
                        <input
                          :disabled="state.registerTeacherKey == ''"
                          type="text"
                          id="floatingInputRegister"
                          class="form-control"
                          v-model="state.registerUsername"
                          placeholder="Username"
                        />
                        <label for="floatingInputRegister">Username</label>
                      </div>
                    </div>

                    <hr />

                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1"
                        ><font-awesome-icon icon="fa-solid fa-key"
                      /></span>
                      <div class="form-floating">
                        <input
                          :disabled="state.registerTeacherKey == ''"
                          :type="[
                            state.showRegisterPassword1 ? 'text' : 'password',
                          ]"
                          id="floatingPassword1Register"
                          class="form-control"
                          v-model="state.registerPassword1"
                          placeholder="Password"
                        />
                        <label for="floatingPassword1Register">Passwort</label>
                      </div>
                      <span class="input-group-text" id="basic-addon1">
                        <a
                          class="greyButton"
                          @mousedown="showRegisterPassword1()"
                          @mouseup="hideRegisterPassword1()"
                          @mouseleave="hideRegisterPassword1()"
                          ><font-awesome-icon
                            v-if="!state.showRegisterPassword1"
                            icon="fa-solid fa-eye-slash" /><font-awesome-icon
                            v-else
                            icon="fa-solid fa-eye" /></a
                      ></span>
                    </div>

                    <div class="input-group mb-3">
                      <span class="input-group-text" id="basic-addon1"
                        ><font-awesome-icon icon="fa-solid fa-key"
                      /></span>
                      <div class="form-floating">
                        <input
                          :disabled="state.registerTeacherKey == ''"
                          :type="[
                            state.showRegisterPassword2 ? 'text' : 'password',
                          ]"
                          id="floatingPassword2Register"
                          class="form-control"
                          v-model="state.registerPassword2"
                          placeholder="Password"
                        />
                        <label for="floatingPassword2Register"
                          >Passwort wiederholen</label
                        >
                      </div>
                      <span class="input-group-text" id="basic-addon1">
                        <a
                          class="greyButton"
                          @mousedown="showRegisterPassword2()"
                          @mouseup="hideRegisterPassword2()"
                          @mouseleave="hideRegisterPassword2()"
                          ><font-awesome-icon
                            v-if="!state.showRegisterPassword2"
                            icon="fa-solid fa-eye-slash" /><font-awesome-icon
                            v-else
                            icon="fa-solid fa-eye" /></a
                      ></span>
                    </div>
                    <div
                      v-if="state.registerIncomplete"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Eingabe unvollst??ndig
                    </div>
                    <div
                      v-if="!registerPasswordsEqual"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Passw??rter nicht identisch
                    </div>
                    <div
                      v-if="registerPasswordTooShort"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Passwort muss mindestens 8 Zeichen enthalten!
                    </div>
                    <div
                      v-if="state.showRegistrationSuccess"
                      class="alert alert-success"
                      role="alert"
                    >
                      Account erfolgreich erstellt. Bitte einloggen.
                    </div>
                    <div
                      v-if="state.showRegistrationError"
                      class="alert alert-danger"
                      role="alert"
                    >
                      Account konnte nicht erstellt werden. M??glicherweise
                      stimmt das Lehrer-Passwort nicht.
                    </div>

                    <button
                      class="btn btn-primary"
                      :class="{
                        disabled: !registerValid || registerPasswordTooShort,
                      }"
                    >
                      Registrieren
                    </button>
                  </form>
                </div>
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

.center-fix {
  height: calc(100vh - 56px);
}
</style>
