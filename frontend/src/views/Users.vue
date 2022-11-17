<script setup>
import { reactive, onMounted, computed, ref, watch } from "vue";
import UserService from "../services/user.service";
import { Modal, Toast } from "bootstrap";

let allUsers = ref([]);

let newPupils = reactive([]);

let state = reactive({
  useUnifiedPassword: true,
  unifiedPassword: "",
  showUnifiedPasswordMissing: false,
  showUniquePasswordMissing: false,
  addNewPupilsLoading: false,
  username_errors: [],
  xAccountsCreated: 0,
});

function preparePupilModal() {
  while (newPupils.length) newPupils.pop();
  addPupilToList();
  state.showUnifiedPasswordMissing = false;
  state.showUniquePasswordMissing = false;
}

function addPupilToList() {
  newPupils.push({ fullname: "", username: "", password: "" });
}

function createPupilAccounts() {
  if (state.useUnifiedPassword && state.unifiedPassword == "") {
    state.showUnifiedPasswordMissing = true;
    return;
  }
  if (!state.useUnifiedPassword) {
    newPupils.forEach((p) => {
      console.log(p);
      if (p.username != "" && p.password == "") {
        state.showUniquePasswordMissing = true;
        return;
      }
    });
  }

  state.addNewPupilsLoading = true;

  //unified password? -> set this password for every new user
  if (state.useUnifiedPassword) {
    newPupils.forEach((p) => {
      p.password = state.unifiedPassword;
    });
  }

  //remove all pupils that don't have a username (password was already checked above)
  for (let i = newPupils.length - 1; i >= 0; i--) {
    if (newPupils[i].username == "") {
      newPupils.splice(i, 1);
    }
  }

  UserService.registerPupils(newPupils).then(
    (response) => {
      // close modal
      var elem = document.getElementById("addPupilsModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      console.log(response.data);

      if (response.data.accounts_created == response.data.accounts_received) {
        const toast = new Toast(
          document.getElementById("toastAllAccountsCreated")
        );
        toast.show();
      } else if (response.data.accounts_created) {
        state.xAccountsCreated = response.data.accounts_created;
        const toast = new Toast(
          document.getElementById("toastXAccountsCreated")
        );
        toast.show();
      }

      if (response.data.username_errors.length) {
        state.username_errors = response.data.username_errors;
        const toast = new Toast(
          document.getElementById("toastErrorAccountsCreated")
        );
        toast.show();
      }

      state.addNewPupilsLoading = false;
    },
    (error) => {
      state.addNewPupilsLoading = false;
    }
  );
}

watch(newPupils, () => {
  if (!newPupils.length) return;
  if (newPupils[newPupils.length - 1].username != "") {
    addPupilToList();
  }
});

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
  <div aria-live="polite" aria-atomic="true" class="position-relative">
    <div class="toast-container bottom-0 end-0 p-3">
      <div
        class="toast align-items-center text-bg-success border-0"
        id="toastAllAccountsCreated"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">Es wurden <b>alle</b> Accounts erstellt.</div>
        </div>
      </div>
      <!-- </div> -->

      <!-- <div class="toast-container bottom-0 end-0 p-3"> -->
      <div
        class="toast align-items-center text-bg-success border-0"
        id="toastXAccountsCreated"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            Es wurden <b>{{ state.xAccountsCreated }}</b> Accounts erstellt.
          </div>
        </div>
      </div>
      <!-- </div> -->

      <!-- <div class="toast-container bottom-0 end-0 p-3"> -->
      <div
        class="toast text-bg-danger"
        id="toastErrorAccountsCreated"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        data-bs-autohide="false"
      >
        <div class="toast-body">
          Folgende Accounts konnten nicht erstellt werden. Vielleicht existieren
          sie bereits?<br />
          <ul>
            <li v-for="u in state.username_errors">{{ u }}</li>
          </ul>
          <div class="mt-2 pt-2 border-top">
            <button
              type="button"
              class="btn btn-secondary btn-sm"
              data-bs-dismiss="toast"
            >
              Schließen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="addPupilsModal"
    data-bs-backdrop="static"
    tabindex="-1"
    aria-labelledby="addPupilsModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-scrollable modal-xl">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="addPupilsModalLabel">
            Schüler-Accounts hinzufügen
          </h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div class="container">
            <div class="row justify-content-start mb-5">
              <div class="col-4 form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="useUnifiedPassword"
                  v-model="state.useUnifiedPassword"
                  checked
                />
                <label class="form-check-label" for="useUnifiedPassword"
                  >Dasselbe Passwort für alle Accounts</label
                >
              </div>
              <div class="col-4">
                <div class="form-floating" v-if="state.useUnifiedPassword">
                  <input
                    v-model="state.unifiedPassword"
                    type="text"
                    class="form-control"
                    placeholder="Einheitliches Passwort für alle Accounts"
                    id="unifiedPasswordLabel"
                  />
                  <label for="unifiedPasswordLabel"
                    >Einheitliches Passwort für alle Accounts</label
                  >
                </div>
              </div>
            </div>
          </div>

          <div
            class="row mb-3"
            v-for="(pupil, index) in newPupils"
            :key="index"
          >
            <div class="form-group col-md-1 text-center">
              <label></label>
              <div>
                <span v-if="pupil.username != ''">{{ index + 1 }}</span
                >&nbsp;
                <span
                  v-if="
                    pupil.username != '' &&
                    ((!state.useUnifiedPassword && pupil.password != '') ||
                      (state.useUnifiedPassword && state.unifiedPassword != ''))
                  "
                  class="text-success"
                  ><font-awesome-icon icon="fa-solid fa-check"
                /></span>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  v-model="pupil.fullname"
                  :id="'fullname_' + index"
                  type="text"
                  class="form-control"
                  placeholder="Vor- und Nachname"
                />
                <label :for="'fullname_' + index">Vor- und Nachname</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  v-model="pupil.username"
                  type="text"
                  class="form-control"
                  placeholder="Benutzername"
                  :id="'username_' + index"
                />
                <label :for="'username_' + index">Benutzername*</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating" v-if="!state.useUnifiedPassword">
                <input
                  v-model="pupil.password"
                  type="text"
                  class="form-control"
                  placeholder="Passwort"
                  :id="'password_' + index"
                />
                <label :for="'password_' + index">Passwort</label>
              </div>
            </div>
          </div>
          <div
            v-if="state.showUnifiedPasswordMissing"
            class="alert alert-danger alert-dismissible"
            role="alert"
          >
            Kein einheitliches Passwort festgelegt!
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              @click.prevent="state.showUnifiedPasswordMissing = false"
            ></button>
          </div>
          <div
            v-if="state.showUniquePasswordMissing"
            class="alert alert-danger alert-dismissible"
            role="alert"
          >
            Ein einzelnes Passwort fehlt!
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              @click.prevent="state.showUniquePasswordMissing = false"
            ></button>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Schließen
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click.prevent="createPupilAccounts()"
            :disabled="state.addNewPupilsLoading"
          >
            <span
              class="spinner-border spinner-border-sm"
              role="status"
              aria-hidden="true"
              v-if="state.addNewPupilsLoading"
            ></span>
            Save changes
          </button>
        </div>
      </div>
    </div>
  </div>

  <h1 class="text-center">Benutzerverwaltung</h1>
  <div class="btn-group non-flex" role="group">
    <button
      type="button"
      class="btn btn-success"
      data-bs-toggle="modal"
      data-bs-target="#addPupilsModal"
      @click="preparePupilModal()"
    >
      <font-awesome-icon icon="fa-solid fa-user-plus" /> Schüler-Accounts
      erstellen
    </button>
    <button type="button" class="btn btn-primary">Klassen verwalten</button>
  </div>

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

<style scoped>
.non-flex {
  display: block;
}

.dark-text {
  color: var(--bs-dark);
}
</style>
