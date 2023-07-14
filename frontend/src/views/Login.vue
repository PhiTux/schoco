<script setup>
import { reactive, computed, onMounted, onBeforeMount } from "vue";
import { useAuthStore } from "../stores/auth.store.js";
import UserService from "../services/user.service.js";
import { useRoute, useRouter } from "vue-router";
import { Toast } from "bootstrap";
import { version } from "../../package.json"
import PasswordInput from "../components/PasswordInput.vue"
import PasswordInfo from "../components/PasswordInfo.vue"

const router = useRouter();

const state = reactive({
  loginIncomplete: false,
  registerIncomplete: false,
  showLoginError: false,
  showRegistrationSuccess: false,
  backendVersion: "",
});

const login = reactive({
  username: "",
  password: "",
})

const register = reactive({
  teacherKey: "",
  name: "",
  username: "",
  password1: "",
  password2: "",
})

onBeforeMount(() => {
  UserService.getVersion().then(
    (response) => {
      state.backendVersion = response.data
    }, (error) => {
      console.log(error.response)
      state.backendVersion = "unknown"
    }
  )
})

onMounted(() => {
  let route = useRoute()
  if (route.query.token_expired) {
    const toast = new Toast(
      document.getElementById("toastTokenExpiredError")
    );
    toast.show();
  }
  router.replace({ query: {} });

  document.title = "Login"
})

async function loginUser() {
  if (!loginValid) {
    state.loginIncomplete = true;
    return;
  }
  const authStore = useAuthStore();
  const result = await authStore.login(
    login.username,
    login.password
  );
  if (result && result.response.status == 401) {
    state.loginIncomplete = false;
    state.showLoginError = true;
  }
}

function registerTeacher() {
  if (
    !registerValid.value ||
    !registerPasswordsEqual.value ||
    registerPasswordTooShort.value
  ) {
    state.registerIncomplete = true;
    return;
  }
  UserService.registerTeacher(
    register.teacherKey,
    register.name,
    register.username,
    register.password1
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

const registerValid = computed(() => {
  let tmp =
    register.teacherKey !== "" &&
    register.name !== "" &&
    register.username !== "" &&
    register.password1 !== "" &&
    register.password2 !== "";
  if (tmp) state.registerIncomplete = false;
  return tmp;
});

const loginValid = computed(() => {
  var tmp = login.username != "" && login.password != "";
  if (tmp) state.loginIncomplete = false;
  return tmp;
});

const registerPasswordsEqual = computed(() => {
  return register.password1 === register.password2;
});

const registerPasswordTooShort = computed(() => {
  return (
    register.password1.length > 0 && register.password1.length < 8
  );
});
</script>

<template>
  <div>
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastTokenExpiredError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Deine Sitzung ist abgelaufen. Du musst dich erneut anmelden.
          </div>
        </div>
      </div>
    </div>
    <div class="center-fix d-flex flex-column">
      <div class="container-fluid flex-fill align-items-center d-flex justify-content-center">
        <div class="w-100 row text-center align-items-center">
          <div class="col-6">
            <div class="container-lg">
              <div class="schoco-icon">{🍫}</div>
              SCHOCO<br />
              <b><u>SCH</u></b>ool <b><u>O</u></b>nline <b><u>CO</u></b>ding
            </div>
          </div>
          <div class="col-6 col-xxl-4">
            <div class="accordion" id="loginAccordion">
              <div class="accordion-item">
                <h2 class="accordion-header" id="headingOne">
                  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne"
                    aria-expanded="true" aria-controls="collapseOne">
                    Login
                  </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne"
                  data-bs-parent="#loginAccordion">
                  <div class="accordion-body">
                    <form @submit.prevent="loginUser()">
                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-user" fixed-width /></span>
                        <div class="form-floating">
                          <input type="text" id="floatingInputLogin" class="form-control" v-model="login.username"
                            placeholder="Username" autofocus />
                          <label for="floatingInputLogin">Username</label>
                        </div>
                      </div>

                      <PasswordInput v-model="login.password" description="Passwort" />

                      <div v-if="state.loginIncomplete" class="alert alert-danger" role="alert">
                        Eingabe unvollständig
                      </div>
                      <div v-if="state.showLoginError" class="alert alert-danger" role="alert">
                        Falscher Benutzername oder Passwort
                      </div>

                      <button class="btn btn-primary" :class="{ disabled: !loginValid }">
                        Login
                      </button>
                    </form>
                  </div>
                </div>
              </div>
              <div class="accordion-item">
                <h2 class="accordion-header" id="headingTwo">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                    data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                    Registrierung nur für Lehrkräfte
                  </button>
                </h2>
                <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo"
                  data-bs-parent="#loginAccordion">
                  <div class="accordion-body">
                    <form @submit.prevent="registerTeacher()">
                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-lock" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input type="password" id="floatingInputTeacherKey" class="form-control"
                            v-model="register.teacherKey" placeholder="Lehrer-Passwort" />
                          <label for="floatingInputTeacherKey">Lehrer-Passwort</label>
                        </div>
                      </div>

                      <hr />

                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-signature" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input :disabled="register.teacherKey == ''" type="text" id="floatingInputRegisterName"
                            class="form-control" v-model="register.name" placeholder="Vor- und Nachname" />
                          <label for="floatingInputRegisterName">Vor- und Nachname</label>
                        </div>
                      </div>

                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-user" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input :disabled="register.teacherKey == ''" type="text" id="floatingInputRegister"
                            class="form-control" v-model="register.username" placeholder="Username" />
                          <label for="floatingInputRegister">Username</label>
                        </div>
                      </div>

                      <hr />

                      <PasswordInfo />

                      <PasswordInput v-model="register.password1" description="Passwort" />

                      <PasswordInput v-model="register.password2" description="Passwort" />

                      <div v-if="state.registerIncomplete" class="alert alert-danger" role="alert">
                        Eingabe unvollständig
                      </div>
                      <div v-if="!registerPasswordsEqual" class="alert alert-danger" role="alert">
                        Passwörter nicht identisch
                      </div>
                      <div v-if="registerPasswordTooShort" class="alert alert-danger" role="alert">
                        Passwort muss mindestens 8 Zeichen enthalten!
                      </div>
                      <div v-if="state.showRegistrationSuccess" class="alert alert-success" role="alert">
                        Account erfolgreich erstellt. Bitte einloggen.
                      </div>
                      <div v-if="state.showRegistrationError" class="alert alert-danger" role="alert">
                        Account konnte nicht erstellt werden. Möglicherweise
                        stimmt das Lehrer-Passwort nicht.
                      </div>

                      <button class="btn btn-primary" :class="{
                        disabled: !registerValid || registerPasswordTooShort,
                      }">
                        Registrieren
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="position-absolute bottom-0 end-0">
          <a href="https://hub.docker.com/r/phitux/schoco-backend/tags">Backend: {{ state.backendVersion }}</a><br />
          <a href="https://hub.docker.com/r/phitux/schoco-nginx/tags">Frontend: {{ version }}</a>
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

.schoco-icon {
  font-size: 80px;
}

.center-fix {
  height: calc(100vh - 56px);
}
</style>
