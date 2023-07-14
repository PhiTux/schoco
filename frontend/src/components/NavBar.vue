<script setup>
import { useAuthStore } from "../stores/auth.store.js";
import { useRoute } from "vue-router";
import { Modal, Toast } from "bootstrap";
import { reactive, computed, onMounted } from "vue";
import UserService from "../services/user.service.js"
import PasswordInput from "./PasswordInput.vue";
import PasswordInfo from "./PasswordInfo.vue";

const authStore = useAuthStore();
const route = useRoute();

let state = reactive({
  oldPassword: "",
  newPassword1: "",
  newPassword2: "",
  isChangingPassword: false,
  passwordInvalidResponse: false,
})

async function logout() {
  const authStore = useAuthStore();
  return authStore.logout();
}

function openPasswordModal() {
  state.oldPassword = "";
  state.newPassword1 = "";
  state.newPassword2 = "";

  // open Modal
  var modal = new Modal(document.getElementById("changePasswordModal"));
  modal.show();
}

const passwordInvalid = computed(() => {
  return state.newPassword1.length < 8
    || !passwordsEqual.value
})

const passwordTooShort = computed(() => {
  return state.newPassword1.length > 0 && state.newPassword1.length < 8
})

const passwordsEqual = computed(() => {
  return state.newPassword1 === state.newPassword2
})

function changePassword() {
  if (passwordInvalid.value || state.isChangingPassword) return;

  state.passwordInvalidResponse = false;
  state.isChangingPassword = true;

  UserService.changePassword(state.oldPassword, state.newPassword1).then(
    (response) => {
      state.isChangingPassword = false;

      // close modal
      var elem = document.getElementById("changePasswordModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastChangePasswordSuccess")
      );
      toast.show();
    },
    (error) => {
      state.isChangingPassword = false;
      console.log(error.response)

      if (error.response.status === 401) {
        state.passwordInvalidResponse = true;
        return;
      }

      // close modal
      var elem = document.getElementById("changePasswordModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastChangePasswordError")
      );
      toast.show();
    }
  )
}



</script>

<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div class="toast align-items-center text-bg-danger border-0" id="toastChangePasswordError" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Fehler beim Ändern des Passworts.
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-success border-0" id="toastChangePasswordSuccess" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Passwort erfolgreich geändert.
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="changePasswordModal" tabindex="-1" aria-labelledby="changePasswordModalLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">Passwort ändern</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">

          <PasswordInput v-model="state.oldPassword" description="Altes Passwort" focus />

          <PasswordInfo />

          <PasswordInput v-model="state.newPassword1" description="Neues Passwort" />

          <PasswordInput v-model="state.newPassword2" description="Neues Passwort" />

          <div v-if="passwordTooShort" class="alert alert-danger" role="alert">
            Passwort muss mindestens 8 Zeichen enthalten.
          </div>

          <div v-if="!passwordsEqual" class="alert alert-danger" role="alert">
            Passwörter nicht identisch.
          </div>

          <div v-if="state.passwordInvalidResponse" class="alert alert-danger" role="alert">
            Eingabe ungültig!
            Stelle sicher, dass dein altes Passwort korrekt ist und dass dein neues Passwort die oberen Kriterien erfüllt.
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
          <button :disabled="passwordInvalid" type="button" class="btn btn-primary" @click.prevent="changePassword()">
            <span v-if="!state.isChangingPassword">Speichern</span>
            <div v-else class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>

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

        <div v-if="authStore.user" class="dropdown">
          <button class="dropdown-toggle btn btn-outline-secondary" href="#" role="button" data-bs-toggle="dropdown"
            aria-expanded="false">
            {{ authStore.user.username }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" @click.prevent="openPasswordModal()">
                <font-awesome-icon icon="fa-solid fa-key" /> Passwort ändern
              </a>
            </li>
            <li class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" @click.prevent="logout()">
                <font-awesome-icon icon="fa-solid fa-right-from-bracket" /> Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.dropdown-item {
  cursor: pointer;
}

ul {
  margin-block-end: 0px !important;
}

.dark-text {
  color: var(--bs-dark);
}
</style>
