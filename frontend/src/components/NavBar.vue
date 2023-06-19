<script setup>
import { useAuthStore } from "../stores/auth.store.js";
import { useRoute } from "vue-router";
import { Modal, Toast } from "bootstrap";
import { reactive, computed, onMounted } from "vue";
import UserService from "../services/user.service.js"

const authStore = useAuthStore();
const route = useRoute();

let state = reactive({
  oldPassword: "",
  newPassword1: "",
  newPassword2: "",
  showOldPassword: false,
  showNewPassword1: false,
  showNewPassword2: false,
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
  return state.oldPassword.length < 8
    || state.newPassword1.length < 8 || state.newPassword1 !== state.newPassword2
})

function showOldPassword() {
  state.showOldPassword = true;
}

function hideOldPassword() {
  state.showOldPassword = false;
}

function showNewPassword1() {
  state.showNewPassword1 = true;
}

function hideNewPassword1() {
  state.showNewPassword1 = false;
}

function showNewPassword2() {
  state.showNewPassword2 = true;
}

function hideNewPassword2() {
  state.showNewPassword2 = false;
}

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

onMounted(() => {
  document.getElementById('changePasswordModal').addEventListener('shown.bs.modal', function () {
    document.getElementById('floatingOldPassword').focus()
  })
})



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

          <div class="input-group mb-3">
            <span class="input-group-text" id="basic-addon1"><font-awesome-icon icon="fa-solid fa-key" /></span>
            <div class="form-floating">
              <input :type="[state.showOldPassword ? 'text' : 'password']" id="floatingOldPassword" class="form-control"
                v-model="state.oldPassword" placeholder="Altes Password" @keyup.enter="changePassword()" />
              <label for="floatingOldPassword">Altes Password</label>
            </div>
            <span class="input-group-text" id="basic-addon1">
              <a class="greyButton" @mousedown="showOldPassword()" @mouseup="hideOldPassword()"
                @mouseleave="hideOldPassword()"><font-awesome-icon v-if="!state.showOldPassword"
                  icon="fa-solid fa-eye-slash" fixed-width /><font-awesome-icon v-else icon="fa-solid fa-eye"
                  fixed-width /></a></span>
          </div>

          <div class="alert alert-info" role="alert">
            Stelle sicher, dass das neue Passwort mindestens 8 Zeichen lang ist und mindestens <b><ins>zwei</ins></b>
            der drei folgenden Kriterien erfüllt:
            <ul>
              <li>Enthält einen Buchstabe</li>
              <li>Enthält eine Zahl</li>
              <li>Enthält ein Sonderzeichen</li>
            </ul>
          </div>

          <div class="input-group mb-3">
            <span class="input-group-text" id="basic-addon1"><font-awesome-icon icon="fa-solid fa-key" /></span>
            <div class="form-floating">
              <input :type="[state.showNewPassword1 ? 'text' : 'password']" id="floatingNewPassword1" class="form-control"
                v-model="state.newPassword1" placeholder="Neues Password" @keyup.enter="changePassword()" />
              <label for="floatingNewPassword1">Neues Password</label>
            </div>
            <span class="input-group-text" id="basic-addon1">
              <a class="greyButton" @mousedown="showNewPassword1()" @mouseup="hideNewPassword1()"
                @mouseleave="hideNewPassword1()"><font-awesome-icon v-if="!state.showNewPassword1"
                  icon="fa-solid fa-eye-slash" fixed-width /><font-awesome-icon v-else icon="fa-solid fa-eye"
                  fixed-width /></a></span>
          </div>

          <div class="input-group mb-3">
            <span class="input-group-text" id="basic-addon1"><font-awesome-icon icon="fa-solid fa-key" /></span>
            <div class="form-floating">
              <input :type="[state.showNewPassword2 ? 'text' : 'password']" id="floatingNewPassword2" class="form-control"
                v-model="state.newPassword2" placeholder="Neues Password bestätigen" @keyup.enter="changePassword()" />
              <label for="floatingNewPassword2">Neues Password bestätigen</label>
            </div>
            <span class="input-group-text" id="basic-addon1">
              <a class="greyButton" @mousedown="showNewPassword2()" @mouseup="hideNewPassword2()"
                @mouseleave="hideNewPassword2()"><font-awesome-icon v-if="!state.showNewPassword2"
                  icon="fa-solid fa-eye-slash" fixed-width /><font-awesome-icon v-else icon="fa-solid fa-eye"
                  fixed-width /></a></span>
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
