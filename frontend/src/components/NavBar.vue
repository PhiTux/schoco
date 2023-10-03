<script setup>
import { useAuthStore } from "../stores/auth.store.js";
import { useRoute } from "vue-router";
import { Modal, Toast } from "bootstrap";
import { reactive, computed, onMounted } from "vue";
import UserService from "../services/user.service.js"
import PasswordInput from "./PasswordInput.vue";
import PasswordInfo from "./PasswordInfo.vue";
import ColorModeSwitch from "./ColorModeSwitch.vue";
import { version } from "../../package.json"

const authStore = useAuthStore();
const route = useRoute();

let state = reactive({
  oldPassword: "",
  newPassword1: "",
  newPassword2: "",
  isChangingPassword: false,
  passwordInvalidResponse: false,
  latestVersion: "0.0.0",
  skipVersion: "0.0.0",
})

onMounted(() => {
  if (!authStore.isTeacher()) return;

  UserService.getLatestVersion().then(
    (response) => {
      state.latestVersion = response.data.latest_version;
      state.skipVersion = response.data.skip_version;
    },
    (error) => {
      console.log(error.response)
    }
  )
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

function skip_latest_version() {
  UserService.skipLatestVersion(state.latestVersion).then(
    (response) => {
      if (response.data.success) {
        state.skipVersion = state.latestVersion;

        // show toast
        const toast = new Toast(
          document.getElementById("toastSkipVersionSuccess")
        );
        toast.show();
      }
      else {
        // show toast
        const toast = new Toast(
          document.getElementById("toastSkipVersionError")
        );
        toast.show();
      }

      // close modal
      var elem = document.getElementById("updateNotification");
      var modal = Modal.getInstance(elem);
      modal.hide();

    },
    (error) => {
      console.log(error.response)
      // close modal
      var elem = document.getElementById("updateNotification");
      var modal = Modal.getInstance(elem);
      modal.hide();

      // show toast
      const toast = new Toast(
        document.getElementById("toastSkipVersionError")
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
          {{ $t("error_changing_password") }}
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-success border-0" id="toastChangePasswordSuccess" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          {{ $t("success_changing_password") }}
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-danger border-0" id="toastSkipVersionError" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i18n-t keypath="error_skipping_version" tag="span">
            {{ state.skipVersion }}
          </i18n-t>
        </div>
      </div>
    </div>

    <div class="toast align-items-center text-bg-success border-0" id="toastSkipVersionSuccess" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i18n-t keypath="success_skipping_version" tag="span">
            {{ state.skipVersion }}
          </i18n-t>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="changePasswordModal" tabindex="-1" aria-labelledby="changePasswordModalLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">{{ $t("change_password") }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">

          <PasswordInput v-model="state.oldPassword" :description="$t('current_password')" id="pwd1" focus />

          <PasswordInfo />

          <PasswordInput v-model="state.newPassword1" :description="$t('new_password')" id="pwd2" />

          <PasswordInput v-model="state.newPassword2" :description="$t('new_password')" id="pwd3" />

          <div v-if="passwordTooShort" class="alert alert-danger" role="alert">
            {{ $t("password_at_least_8") }}
          </div>

          <div v-if="!passwordsEqual" class="alert alert-danger" role="alert">
            {{ $t("passwords_not_identical") }}
          </div>

          <div v-if="state.passwordInvalidResponse" class="alert alert-danger" role="alert"
            v-html="$t('password_change_invalid')" />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{{ $t("abort") }}</button>
          <button :disabled="passwordInvalid" type="button" class="btn btn-primary" @click.prevent="changePassword()">
            <span v-if="!state.isChangingPassword">{{ $t("save") }}</span>
            <div v-else class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="updateNotification" tabindex="-1" aria-labelledby="updateNotificationLabel"
    aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">{{ $t("update_available") }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          {{ $t("update_available_text") }}:
          <ul>
            <li>
              {{ $t("current_version") }}: <b>{{ version }}</b>
            </li>
            <li>
              {{ $t("latest_version") }}: <b>{{ state.latestVersion }}</b>
            </li>
          </ul>
          <div class="alert alert-warning mt-2">
            <i18n-t keypath="read_the_changelog" tag="span">
              <a href="https://github.com/phitux/schoco#changelog" target="_blank">{{ $t("changelog") }}</a>
            </i18n-t>
          </div>

          <hr>

          <div class="alert alert-danger">
            <i18n-t keypath="skip_version_warning" tag="span">
              {{ state.latestVersion }}
            </i18n-t>
            <br>
            <div class="d-flex justify-content-center mt-3">
              <button class="btn btn-outline-danger" @click.prevent="skip_latest_version()">
                <i18n-t keypath="skip_version_x">
                  {{ state.latestVersion }}
                </i18n-t>
              </button>
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal">{{ $t("got_it") }}</button>
        </div>
      </div>
    </div>
  </div>

  <nav class="navbar fixed-top navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/home">{🍫}<span class="ms-2">{{ $t("home_title") }}</span></router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

          <router-link v-if="authStore.isTeacher() && route.name !== 'users'" class="btn btn-outline-secondary ms-2"
            to='/users'>
            <font-awesome-icon icon="fa-solid fa-users" fixed-width /> {{ $t("usermanagement") }}
          </router-link>
        </ul>

        <button v-if="state.latestVersion != state.skipVersion && authStore.isTeacher() && version != state.latestVersion"
          data-bs-toggle="modal" data-bs-target="#updateNotification" type="button"
          class="btn btn-outline-warning me-2 rounded-circle d-flex justify-content-center versionBtn">
          <span><font-awesome-icon icon="fa-solid fa-triangle-exclamation" fixed-width />
          </span>
        </button>

        <ColorModeSwitch class="me-2" />

        <div v-if="authStore.user" class="dropdown">
          <button class="dropdown-toggle btn btn-outline-secondary" href="#" role="button" data-bs-toggle="dropdown"
            aria-expanded="false">
            {{ authStore.user.username }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end" data-bs-theme="light">
            <li>
              <a class="dropdown-item" @click.prevent="openPasswordModal()">
                <font-awesome-icon icon="fa-solid fa-key" fixed-width /> {{ $t("change_password") }}
              </a>
            </li>
            <li class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" @click.prevent="logout()">
                <font-awesome-icon icon="fa-solid fa-right-from-bracket" fixed-width /> {{ $t("logout") }}
              </a>
            </li>
          </ul>
        </div>


      </div>
    </div>
  </nav>
</template>

<style scoped>
.versionBtn {
  width: 38px;
}

.dropdown-item {
  cursor: pointer;
}

ul {
  margin-block-end: 0px !important;
}
</style>
