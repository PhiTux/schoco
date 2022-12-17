<script setup>
import { reactive, onMounted, computed, ref, watch } from "vue";
import UserService from "../services/user.service";
import { Modal, Toast } from "bootstrap";
import { useAuthStore } from "../stores/auth.store";
import CourseBadge from "../components/CourseBadge.vue";

let allUsers = ref([]);

let allCourses = ref([]);

let newPupils = reactive([]);

let state = reactive({
  useUnifiedPassword: true,
  unifiedPassword: "",
  showUnifiedPasswordMissing: false,
  showUniquePasswordMissing: false,
  addNewPupilsLoading: false,
  username_errors: [],
  xAccountsCreated: 0,
  searchName: "",
  changePasswordFullname: "",
  changePasswordUsername: "",
  newPassword: "",
  showNewPassword: false,
  changePasswordLoading: false,
  showPasswordTooShort: false,
  newCourseColor: "#ff8000",
  newCourseName: "",
  newCourseFontDark: false,
  deleteUserFullname: "",
  deleteUserUsername: "",
  deleteUserId: 0,
});

function preparePupilModal() {
  while (newPupils.length) newPupils.pop();
  addPupilToList();
  state.showUnifiedPasswordMissing = false;
  state.showUniquePasswordMissing = false;
  state.showPasswordTooShort = false;
}

function addPupilToList() {
  newPupils.push({ fullname: "", username: "", password: "" });
}

function createPupilAccounts() {
  if (state.useUnifiedPassword) {
    if (state.unifiedPassword == "") {
      state.showUnifiedPasswordMissing = true;
      return;
    } else if (state.unifiedPassword.length < 8) {
      state.showPasswordTooShort = true;
      return;
    }
  }
  if (!state.useUnifiedPassword) {
    for (const p of newPupils) {
      if (p.username != "") {
        if (p.password == "") {
          state.showUniquePasswordMissing = true;
          return;
        } else if (p.password.length < 8) {
          state.showPasswordTooShort = true;
          return;
        }
      }
    }
  }

  state.addNewPupilsLoading = true;

  //unified password? -> set this password for every new user
  if (state.useUnifiedPassword) {
    newPupils.forEach((p) => {
      p.password = state.unifiedPassword;
    });
  }

  //remove all pupils that don't have a fullname or username (password was already checked above)
  for (let i = newPupils.length - 1; i >= 0; i--) {
    if (newPupils[i].fullname == "" || newPupils[i].username == "") {
      newPupils.splice(i, 1);
    }
  }

  UserService.registerPupils(newPupils).then(
    (response) => {
      getAllUsers();

      // close modal
      var elem = document.getElementById("addPupilsModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

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
      if (error.response.status == 403) {
        const user = useAuthStore();
        user.logout();
      } else console.log(error);
    }
  );
}

function openModalDeleteUser(id) {
  for (var i = 0; i < allUsers.value.length; i++) {
    if (allUsers.value[i].id == id) {
      state.deleteUserFullname = allUsers.value[i].full_name;
      state.deleteUserUsername = allUsers.value[i].username;
      state.deleteUserId = id;
      break;
    }
  }
}

function deleteUser() {
  UserService.deleteUser(state.deleteUserId).then(
    (response) => {
      var elem = document.getElementById("DeleteUserModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastDeleteUserSuccess")
        );
        toast.show();

        getAllUsers();
      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteUserError")
        );
        toast.show();
      }
    },
    (error) => {
      var elem = document.getElementById("DeleteUserModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      console.log(error);
      const toast = new Toast(document.getElementById("toastDeleteUserError"));
      toast.show();
    }
  );
}

function openModalChangePassword(id) {
  state.newPassword = "";
  state.showNewPassword = false;
  state.changePasswordLoading = false;
  state.showPasswordTooShort = false;

  allUsers.value.every((u) => {
    if (u.id == id) {
      state.changePasswordFullname = u.full_name;
      state.changePasswordUsername = u.username;
      return false;
    }
    return true;
  });
}

function changePassword() {
  if (state.newPassword.length < 8) {
    state.showPasswordTooShort = true;
    return;
  }
  state.showPasswordTooShort = false;

  state.changePasswordLoading = true;

  UserService.setNewPassword(
    state.changePasswordUsername,
    state.newPassword
  ).then(
    (response) => {
      state.changePasswordLoading = false;

      var elem = document.getElementById("changePasswordModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastSuccessPasswordChanged")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastPasswordChangeError")
        );
        toast.show();
      }
    },
    (error) => {
      console.log(error);
      const toast = new Toast(
        document.getElementById("toastPasswordChangeError")
      );
      toast.show();
    }
  );
}

function addNewCourse() {
  if (state.newCourseColor == "" || state.newCourseName == "") return;

  UserService.addNewCourse(
    state.newCourseName,
    state.newCourseColor,
    state.newCourseFontDark
  ).then(
    (response) => {
      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastSuccessCourseCreated")
        );
        toast.show();

        getAllCourses();
      } else {
        const toast = new Toast(
          document.getElementById("toastErrorCourseCreated")
        );
        toast.show();
        console.log(response.data);
      }
    },
    (error) => {
      const toast = new Toast(
        document.getElementById("toastErrorCourseCreated")
      );
      toast.show();
      console.log(error);
    }
  );
}

function addCourseToUser(user_id, coursename) {
  UserService.addCourseToUser(user_id, coursename).then(
    (response) => {
      if (response.data.success) {
        getAllUsers();
      } else {
        console.log(response.data.message);
      }
    },
    (error) => {
      const toast = new Toast(
        document.getElementById("toastErrorAddUserToCourse")
      );
      toast.show();
      console.log(error);
    }
  );
}

function removeCourseFromUser(user_id, course_id) {
  UserService.removeCourseFromUser(user_id, course_id).then(
    (response) => {
      if (response.data.success) {
        getAllUsers();
      } else {
        console.log(response.data.message);
      }
    },
    (error) => {
      console.log(error);
    }
  );
}

function getAllCourses() {
  UserService.getAllCourses().then(
    (response) => {
      allCourses.value = response.data;
    },
    (error) => {
      if (error.response.status == 403) {
        const user = useAuthStore();
        user.logout();
      } else console.log(error);
    }
  );
}

function getAllUsers() {
  UserService.getAllUsers().then(
    (response) => {
      // remove unnecessary attribute 'hashed_password'
      allUsers.value = response.data.users.map(
        ({ hashed_password, ...keepAttrs }) => keepAttrs
      );
      for (const u of allUsers.value) {
        for (const c of response.data.coursesList) {
          if (c.user_id == u.id) {
            u.courses = c.courses;
            break;
          }
        }
      }
    },
    (error) => {
      if (error.response.status == 403) {
        const user = useAuthStore();
        user.logout();
      } else console.log(error);
    }
  );
}

watch(newPupils, () => {
  if (!newPupils.length) return;
  if (
    newPupils[newPupils.length - 1].fullname != "" &&
    newPupils[newPupils.length - 1].username != ""
  ) {
    addPupilToList();
  }
});

onMounted(() => {
  getAllUsers();
  getAllCourses();
});

let allUsersFiltered = computed(() => {
  if (allUsers.value.length == 0) {
    return [];
  }
  return allUsers.value.filter((user) => {
    if (state.searchName == "") return true;
    else
      return (
        user.username.toLowerCase().includes(state.searchName.toLowerCase()) ||
        user.full_name.toLowerCase().includes(state.searchName.toLowerCase())
      );
  });
});

let allUsersFilteredSorted = computed(() => {
  if (!allUsersFiltered) {
    return [];
  }
  return allUsersFiltered.value;
});

function showNewPassword() {
  state.showNewPassword = true;
}

function hideNewPassword() {
  state.showNewPassword = false;
}
</script>

<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div
      class="toast align-items-center text-bg-success border-0"
      id="toastSuccessPasswordChanged"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">Passwort wurde geändert.</div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-danger border-0"
      id="toastPasswordChangeError"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">Fehler beim Ändern des Passworts.</div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-danger border-0"
      id="toastDeleteUserError"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          Benutzer {{ state.deleteUserFullname }} ({{
            state.deleteUserUsername
          }}) konnte nicht gelöscht werden.
        </div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-success border-0"
      id="toastDeleteUserSuccess"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          Benutzer {{ state.deleteUserFullname }} ({{
            state.deleteUserUsername
          }}) wurde erfolgreich gelöscht.
        </div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-success border-0"
      id="toastSuccessCourseCreated"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">Kurs wurde erstellt.</div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-success border-0"
      id="toastSuccessCourseCreated"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">Kurs wurde erstellt.</div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-danger border-0"
      id="toastErrorCourseCreated"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          Fehler beim Erstellen des Kurses. Vielleicht existiert der Kursname
          bereits?
        </div>
      </div>
    </div>

    <div
      class="toast align-items-center text-bg-danger border-0"
      id="toastErrorAddUserToCourse"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          Konnte User nicht zum Kurs zufügen. Ist er bereits Mitglied?
        </div>
      </div>
    </div>

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

  <div
    class="modal fade"
    id="addCoursesModal"
    tabindex="-1"
    aria-labelledby="addCourseModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5">Neuen Kurs erstellen</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div class="mb-3 row">
            <label for="coursename" class="col-sm-4 col-form-label"
              >Kursname</label
            >
            <div class="col-sm-8">
              <input
                type="text"
                class="form-control"
                id="coursename"
                placeholder="Kursname"
                v-model="state.newCourseName"
              />
            </div>
          </div>
          <div class="mb-3 row">
            <label for="coursebackgroundcolor" class="col-sm-4 col-form-label"
              >Hintergrundfarbe</label
            >
            <div class="col-sm-8">
              <input
                type="color"
                class="form-control form-control-color"
                id="coursebackgroundcolor"
                v-model="state.newCourseColor"
                title="Farbe wählen"
              />
            </div>
          </div>
          <div class="mb-3 row">
            <label for="coursefontcolor" class="col-sm-4 col-form-label">
              Schriftfarbe
            </label>
            <div class="col-sm-8" style="margin-top: auto; margin-bottom: auto">
              <div class="d-flex">
                <label class="form-check-label" for="flexSwitchCheckDefault"
                  >hell</label
                >
                <div
                  class="form-check form-switch"
                  style="padding-left: inherit; padding: 0 5px 0 5px"
                >
                  <input
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                    style="margin-left: inherit"
                    id="flexSwitchCheckDefault"
                    v-model="state.newCourseFontDark"
                  />
                </div>
                <label class="form-check-label" for="flexSwitchCheckDefault">
                  dunkel</label
                >
              </div>
            </div>
          </div>

          <hr />

          <div class="mb-3 row">
            <label for="coursepreview" class="col-sm-4 col-form-label"
              ><b>Vorschau</b></label
            >
            <div class="col-sm-2" style="margin-top: auto; margin-bottom: auto">
              <CourseBadge
                :color="state.newCourseColor"
                :font-dark="state.newCourseFontDark"
                :name="state.newCourseName"
              />
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
              @click.prevent="addNewCourse()"
              :disabled="state.newCourseName.length < 2"
            >
              <span
                class="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
                v-if="state.changePasswordLoading"
              ></span>
              Neuen Kurs erstellen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="changePasswordModal"
    tabindex="-1"
    aria-labelledby="changePasswordModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5">Passwort ändern</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body text-center">
          <h4>
            {{ state.changePasswordFullname }} ({{
              state.changePasswordUsername
            }})
          </h4>

          <div class="input-group mb-3">
            <span class="input-group-text" id="basic-addon1"
              ><font-awesome-icon icon="fa-solid fa-key"
            /></span>
            <div class="form-floating">
              <input
                :type="[state.showNewPassword ? 'text' : 'password']"
                id="floatingNewPassword"
                class="form-control"
                v-model="state.newPassword"
                placeholder="Neues Password"
                @keyup.enter="changePassword()"
              />
              <label for="floatingNewPassword">Neues Password</label>
            </div>
            <span class="input-group-text" id="basic-addon1">
              <a
                class="greyButton"
                @mousedown="showNewPassword()"
                @mouseup="hideNewPassword()"
                @mouseleave="hideNewPassword()"
                ><font-awesome-icon
                  v-if="!state.showNewPassword"
                  icon="fa-solid fa-eye-slash" /><font-awesome-icon
                  v-else
                  icon="fa-solid fa-eye" /></a
            ></span>
          </div>

          <div
            v-if="state.showPasswordTooShort"
            class="alert alert-danger alert-dismissible"
            role="alert"
          >
            Passwort muss mindestens 8 Zeichen lang sein!
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              @click.prevent="state.showPasswordTooShort = false"
            ></button>
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
              @click.prevent="changePassword()"
              :disabled="
                state.changePasswordLoading || state.newPassword.length < 8
              "
            >
              <span
                class="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
                v-if="state.changePasswordLoading"
              ></span>
              Neues Passwort speichern
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="DeleteUserModal"
    tabindex="-1"
    aria-labelledby="deleteUserdModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content dark-text">
        <div class="modal-header">
          <h1 class="modal-title fs-5">Benutzer löschen</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body text-center">
          <h4>
            Folgenden Benutzer wirklich löschen?<br />
            <b
              >{{ state.deleteUserFullname }} ({{
                state.deleteUserUsername
              }})</b
            >
          </h4>

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
              @click.prevent="deleteUser()"
            >
              Benutzer löschen
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
            <div class="row mt-2">
              <label class="col-4 col-form-label" for="useUnifiedPassword"
                >Dasselbe Passwort für alle Accounts</label
              >
              <div class="col-1">
                <div class="form-switch form-check pt-2 mb-5">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                    id="useUnifiedPassword"
                    v-model="state.useUnifiedPassword"
                    checked
                  />
                </div>
              </div>
              <div class="col-5">
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

              <div class="col-4"></div>
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
                <span v-if="pupil.fullname != '' || pupil.username != ''">{{
                  index + 1
                }}</span
                >&nbsp;
                <font-awesome-layers
                  v-if="
                    pupil.fullname != '' &&
                    pupil.username != '' &&
                    ((!state.useUnifiedPassword &&
                      pupil.password.length >= 8) ||
                      (state.useUnifiedPassword &&
                        state.unifiedPassword.length >= 8))
                  "
                >
                  <font-awesome-icon
                    icon="fa-circle"
                    style="color: var(--bs-success)"
                  />
                  <font-awesome-icon
                    icon="fa-check"
                    transform="shrink-5"
                    style="color: white"
                  />
                </font-awesome-layers>
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
                <label :for="'username_' + index">Benutzername</label>
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
          <div
            v-if="state.showPasswordTooShort"
            class="alert alert-danger alert-dismissible"
            role="alert"
          >
            Passwort muss mindestens 8 Zeichen lang sein!
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              @click.prevent="state.showPasswordTooShort = false"
            ></button>
          </div>
        </div>
        <div class="alert alert-info text-center" role="alert">
          Nur Zeilen mit grünem Haken
          <span
            ><font-awesome-layers>
              <font-awesome-icon
                icon="fa-circle"
                style="color: var(--bs-success)"
              />
              <font-awesome-icon
                icon="fa-check"
                transform="shrink-5"
                style="color: white"
              /> </font-awesome-layers
          ></span>
          werden berücksichtigt!
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
            Accounts erstellen
          </button>
        </div>
      </div>
    </div>
  </div>

  <h1 class="text-center">Benutzerverwaltung</h1>
  <div class="btn-group non-flex text-center m-4" role="group">
    <button
      type="button"
      class="btn btn-primary"
      data-bs-toggle="modal"
      data-bs-target="#addCoursesModal"
    >
      Kurse erstellen
      <font-awesome-icon icon="fa-solid fa-users" />
    </button>
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
  </div>

  <div class="container">
    <div class="row mb-4 ms-1">
      Kurse:
      <div class="col">
        <CourseBadge
          v-for="c in allCourses"
          :color="c.color"
          :font-dark="c.fontDark"
          :name="c.name"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-3">
        <div class="input-group mb-3">
          <span class="round-left input-group-text" id="basic-addon1">
            <font-awesome-icon icon="fa-solid fa-user"
          /></span>
          <div class="form-floating">
            <input
              type="text"
              id="floatingInputSearchPerson"
              class="form-control round-right"
              v-model="state.searchName"
              placeholder="Personensuche"
            />
            <label class="input-label" for="floatingInputSearchPerson"
              >Personensuche</label
            >
          </div>
        </div>
      </div>
    </div>

    <table class="table table-dark table-striped table-hover align-middle">
      <thead>
        <tr>
          <th scope="col">#id</th>
          <th scope="col">Name</th>
          <th scope="col">Username</th>
          <th scope="col">Kurse</th>
          <th scope="col">Rolle</th>
          <th scope="col">Einstellungen</th>
        </tr>
      </thead>
      <tbody>
        <tr class="py-1" v-for="x in allUsersFilteredSorted">
          <th scope="row">{{ x.id }}</th>
          <td>{{ x.full_name }}</td>
          <td>{{ x.username }}</td>
          <td>
            <CourseBadge
              v-for="c in x.courses"
              :color="c.color"
              :font-dark="c.fontDark"
              :name="c.name"
              :is-deletable="true"
              @remove="removeCourseFromUser(x.id, c.id)"
            />
            <div class="btn-group">
              <a class="btn-round btn" data-bs-toggle="dropdown">
                <font-awesome-layers class="fa-lg">
                  <font-awesome-icon
                    icon="fa-circle"
                    style="color: var(--bs-secondary)"
                  />
                  <div style="color: var(--bs-light)">
                    <font-awesome-icon icon="fa-plus" transform="shrink-6" />
                  </div>
                </font-awesome-layers>
              </a>
              <ul class="dropdown-menu">
                <li v-for="c in allCourses">
                  <a
                    class="dropdown-item btn"
                    @click.prevent="addCourseToUser(x.id, c.name)"
                  >
                    <CourseBadge
                      :color="c.color"
                      :font-dark="c.fontDark"
                      :name="c.name"
                  /></a>
                </li>
              </ul>
            </div>
          </td>
          <td>{{ x.role }}</td>
          <td>
            <a
              class="btn-round btn"
              data-bs-toggle="modal"
              data-bs-target="#changePasswordModal"
              @click.prevent="openModalChangePassword(x.id)"
            >
              <font-awesome-layers class="fa-lg">
                <font-awesome-icon
                  icon="fa-circle"
                  style="color: var(--bs-warning)"
                />
                <div style="color: black">
                  <font-awesome-icon icon="fa-key" transform="shrink-6" />
                </div>
              </font-awesome-layers>
            </a>
            <a
              class="btn-round btn ps-3"
              data-bs-toggle="modal"
              data-bs-target="#DeleteUserModal"
              @click.prevent="openModalDeleteUser(x.id)"
            >
              <font-awesome-layers class="fa-lg">
                <font-awesome-icon
                  icon="fa-circle"
                  style="color: var(--bs-danger)"
                />
                <div style="color: white">
                  <font-awesome-icon icon="fa-trash" transform="shrink-6" />
                </div>
              </font-awesome-layers>
            </a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.round-left {
  border-top-left-radius: var(--bs-border-radius-pill);
  border-bottom-left-radius: var(--bs-border-radius-pill);
}

.round-right {
  border-top-right-radius: var(--bs-border-radius-pill);
  border-bottom-right-radius: var(--bs-border-radius-pill);
}

.input-label {
  color: var(--bs-dark);
}

.btn-round {
  padding: 0;
  border: 0px;
}

.non-flex {
  display: block;
}

.dark-text {
  color: var(--bs-dark);
}
</style>
