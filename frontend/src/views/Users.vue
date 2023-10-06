<script setup>
import { reactive, onMounted, computed, ref, watch } from "vue";
import UserService from "../services/user.service.js";
import { Modal, Toast } from "bootstrap";
import { useAuthStore } from "../stores/auth.store.js";
import CourseBadge from "../components/CourseBadge.vue";
import PasswordInput from "../components/PasswordInput.vue";
import PasswordInfo from "../components/PasswordInfo.vue";
import { useI18n } from 'vue-i18n'
const authStore = useAuthStore();

const i18n = useI18n()

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
  changePasswordLoading: false,
  showPasswordTooShort: false,
  showPasswordInvalid: false,
  showUsernameWhitespaceWarning: false,
  newCourseColor: "#ff8000",
  newCourseName: "",
  deleteUserFullname: "",
  deleteUserUsername: "",
  deleteUserIsTeacher: false,
  deleteUserId: 0,
  confirmPassword: "",
  confirmPasswordInvalid: false,
  isConfirmingPassword: false,
  selectedUser: false,
  edit_user_id: 0,
  edit_user_property: "",
  edited_name: "",
  changingName: false,
  edited_username: "",
  changingUsername: false,
  removeCourseId: 0,
  removeCourseName: "",
  newPupilsToCourses: [],
  editCourseID: 0,
  editCourseColor: "",
  editCourseName: "",
  oldCourseName: "",
  courseLoading: false
});

function selectUser(user) {
  state.selectedUser = user;
}

function unselectUser() {
  state.selectedUser = false
}

function prepareAddCoursesModal() {
  state.courseLoading = false;
}

function preparePupilModal() {
  while (newPupils.length) newPupils.pop();
  addPupilToList();
  state.showUnifiedPasswordMissing = false;
  state.showUniquePasswordMissing = false;
  state.showPasswordTooShort = false;
  state.showUsernameWhitespaceWarning = false;
  while (state.newPupilsToCourses.length) state.newPupilsToCourses.pop();
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
  else {
    for (const p of newPupils) {
      if (p.username === "")
        continue;

      if (p.password === "") {
        state.showUniquePasswordMissing = true;
        return;
      } else if (p.password.length < 8) {
        state.showPasswordTooShort = true;
        return;
      }
    }
  }

  // check if any username contains a space
  for (const p of newPupils) {
    if (p.username.trim().includes(" ")) {
      state.showUsernameWhitespaceWarning = true;
      return;
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
    if (newPupils[i].fullname.trim() == "" || newPupils[i].username.trim() == "") {
      newPupils.splice(i, 1);
    }
  }

  // create array of course-ids to add the new pupils
  var courseIDs = []
  for (let i = 0; i < state.newPupilsToCourses.length; i++) {
    courseIDs.push(state.newPupilsToCourses[i].id)
  }

  UserService.registerPupils(newPupils, courseIDs).then(
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

      if (response.data.course_error) {
        const toast = new Toast(
          document.getElementById("toastErrorAccountsCreatedCourses")
        );
        toast.show();
      }

      state.addNewPupilsLoading = false;
    },
    (error) => {
      if (error.response.status == 403) {
        authStore.logout();
      } else console.log(error);
    }
  );
}

function openModalDeleteUser(id) {
  for (var i = 0; i < allUsers.value.length; i++) {
    if (allUsers.value[i].id == id) {
      state.deleteUserFullname = allUsers.value[i].full_name;
      state.deleteUserUsername = allUsers.value[i].username;
      state.deleteUserIsTeacher = allUsers.value[i].role === 'teacher'
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

const showChangePasswordTooShort = computed(() => {
  return state.newPassword.length > 0 && state.newPassword.length < 8
})

function openModalChangePassword(id) {
  state.newPassword = "";
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

      var elem = document.getElementById("changeUserPasswordModal");
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
      console.log(error.response);
      state.changePasswordLoading = false;

      if (error.response.status == 400) {
        state.showPasswordInvalid = true;
      } else {
        const toast = new Toast(
          document.getElementById("toastPasswordChangeError")
        );
        toast.show();
      }
    }
  );
}

function editCourse() {
  if (state.editCourseColor == "" || state.editCourseName.length < 2 || state.editCourseName.length > 30) return;

  state.courseLoading = true

  UserService.editCourse(
    state.editCourseID,
    state.editCourseName,
    state.editCourseColor,
    editCourseFontDark.value
  ).then(
    (response) => {
      state.courseLoading = false

      //close modal #editCourseModal
      var elem = document.getElementById("editCourseModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastSuccessCourseEdited")
        );
        toast.show();

        getAllCourses();
        getAllUsers();
      } else {
        const toast = new Toast(
          document.getElementById("toastErrorCourseEdited")
        );
        toast.show();
      }
    },
    (error) => {
      console.log(error.response)

      state.courseLoading = false

      //close modal #editCourseModal
      var elem = document.getElementById("editCourseModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastErrorCourseEdited")
      );
      toast.show();
    }
  )
}

function addNewCourse() {
  if (state.newCourseColor == "" || state.newCourseName.length < 2 || state.newCourseName.length > 30) return;

  state.courseLoading = true

  UserService.addNewCourse(
    state.newCourseName,
    state.newCourseColor,
    newCourseFontDark.value
  ).then(
    (response) => {
      state.courseLoading = false

      //close modal #addCoursesModal
      var elem = document.getElementById("addCoursesModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

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
      state.courseLoading = false

      const toast = new Toast(
        document.getElementById("toastErrorCourseCreated")
      );
      toast.show();

      //close modal #addCoursesModal
      var elem = document.getElementById("addCoursesModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

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
      if (error.response) {
        if (error.response.status == 403) {
          authStore.logout();
        } else console.log(error);
      }
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
      if (error.response) {
        if (error.response.status == 403) {
          authStore.logout();
        } else console.log(error);
      }
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

function passwordConfirmed() {
  getAllUsers();
  getAllCourses();

  const modal = Modal.getInstance(
    document.getElementById("confirmPasswordModal")
  );
  modal.hide();
}

function confirmPassword() {
  if (state.isConfirmingPassword) return
  if (!state.confirmPassword.length) {
    state.confirmPasswordInvalid = true;
  }

  state.isConfirmingPassword = true;
  state.confirmPasswordInvalid = false

  UserService.confirmTeacherPassword(state.confirmPassword).then(
    (response) => {
      state.isConfirmingPassword = false;
      if (response.data.success) {
        passwordConfirmed()
      } else {
        state.confirmPasswordInvalid = true
      }
    }, (error) => {
      const toast = new Toast(
        document.getElementById("toastErrorConfirmPassword")
      );
      toast.show();
      console.log(error.response)
    }
  )
}

onMounted(() => {
  //confirm Password:
  const modal = new Modal(document.getElementById("confirmPasswordModal"));
  modal.show();

  document.title = i18n.t("usermanagement")
});

function calculateFontDark(color) {
  let r = color.slice(1, 3)
  let g = color.slice(3, 5)
  let b = color.slice(5, 7)

  if (parseInt(r, 16) * 0.299 + parseInt(g, 16) * 0.587 + parseInt(b, 16) * 0.114 > 156)
    return true

  return false
}

let newCourseFontDark = computed(() => {
  return calculateFontDark(state.newCourseColor)
});

let editCourseFontDark = computed(() => {
  return calculateFontDark(state.editCourseColor)
})

let allUsersFiltered = computed(() => {
  if (allUsers.value.length == 0) {
    return [];
  }
  return allUsers.value.filter((user) => {
    if (state.searchName == "") return true;

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

function edit_user(id, property, content) {
  state.edit_user_id = id;
  state.edit_user_property = property;
  if (property === "name") {
    state.edited_name = content
  } else if (property === "username") {
    state.edited_username = content
  }
}

function abort_edit_user() {
  state.edit_user_id = 0;
  state.edit_user_property = ""
}

function change_name(id) {
  if (state.edited_name.trim() == "") {
    const toast = new Toast(
      document.getElementById("toastUpdateNameEmpty")
    );
    toast.show();
    return
  }

  state.changingName = true
  UserService.changeName(id, state.edited_name.trim()).then(
    response => {
      if (response.data) {
        for (let i = 0; i < allUsers.value.length; i++) {
          if (allUsers.value[i].id == id) {
            allUsers.value[i].full_name = state.edited_name.trim()
            break
          }
        }

      }
      state.changingName = false
      abort_edit_user()
    },
    error => {
      state.changingName = false
      abort_edit_user()
      console.log(error.response)
    })
}

function change_username(id) {
  if (state.edited_username.trim() == "") {
    const toast = new Toast(
      document.getElementById("toastUpdateNameEmpty")
    );
    toast.show();
    return
  }

  state.changingUsername = true
  UserService.changeUsername(id, state.edited_username.trim()).then(
    response => {
      if (response.data.last_username.length) {
        for (let i = 0; i < allUsers.value.length; i++) {
          if (allUsers.value[i].id == id) {
            allUsers.value[i].username = state.edited_username.trim()
            break
          }
        }

        if (response.data.last_username === authStore.user.username) {
          authStore.logout_username_changed();
        }
      } else {
        const toast = new Toast(
          document.getElementById("toastUsernameChangeError")
        );
        toast.show();
      }

      state.changingUsername = false
      abort_edit_user()
    },
    error => {
      state.changingUsername = false
      abort_edit_user()
      console.log(error.response)
    })
}


function removeCourse() {
  UserService.removeCourse(state.removeCourseId).then(
    (response) => {
      const modal = Modal.getInstance(
        document.getElementById("removeCourseModal")
      );
      modal.hide();

      if (response.data.success) {
        getAllCourses();
        getAllUsers();
        const toast = new Toast(
          document.getElementById("toastSuccessCourseRemoved")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastErrorCourseRemoved")
        );
        toast.show();
      }
    },
    (error) => {
      console.log(error.response)
      const modal = Modal.getInstance(
        document.getElementById("removeCourseModal")
      );
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastErrorCourseRemoved")
      );
      toast.show();
    }
  )
}


function openModalRemoveCourse(id) {
  state.removeCourseId = id
  //get coursename from allcourses by id
  allCourses.value.forEach(course => {
    if (course.id == id) {
      state.removeCourseName = course.name
    }
  })

  const modal = new Modal(document.getElementById("removeCourseModal"));
  modal.show();
}

function openModalEditCourse(id) {
  state.courseLoading = false

  state.editCourseID = id
  for (let i = 0; i < allCourses.value.length; i++) {
    if (allCourses.value[i].id == id) {
      state.oldCourseName = allCourses.value[i].name
      state.editCourseName = allCourses.value[i].name
      state.editCourseColor = allCourses.value[i].color
    }
  }

  const modal = new Modal(document.getElementById("editCourseModal"));
  modal.show();
}

function addCourseToNewPupils(id) {
  // check if course already selected
  for (const e of state.newPupilsToCourses) {
    if (e.id == id) {
      return;
    }
  }

  for (let i = 0; i < allCourses.value.length; i++) {
    if (allCourses.value[i].id == id) {
      state.newPupilsToCourses.push(allCourses.value[i]);
      break
    }
  }
}

function removeCourseFromNewPupils(id) {
  for (let i = 0; i < state.newPupilsToCourses.length; i++) {
    if (state.newPupilsToCourses[i].id == id) {
      state.newPupilsToCourses.splice(i, 1)
      break
    }
  }
}
</script>

<template>
  <div>
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastErrorConfirmPassword" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("error_confirming_password") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateNameEmpty" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("name_must_not_be_empty") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastSuccessPasswordChanged" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("password_changed_success") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastPasswordChangeError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("password_changed_error") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUsernameChangeError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("error_on_changing_username") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteUserError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i18n-t keypath="couldnt_delete_user" tag="span">
              <span>{{ state.deleteUserFullname }}</span>
              <span>({{ state.deleteUserUsername }})</span>
            </i18n-t>
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDeleteUserSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i18n-t keypath="delete_user_success" tag="span">
              <span>{{ state.deleteUserFullname }}</span>
              <span>({{ state.deleteUserUsername }})</span>
            </i18n-t>
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastSuccessCourseCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("course_created_success") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastErrorCourseCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("course_created_error") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastSuccessCourseEdited" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("course_edited_success") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastErrorCourseEdited" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("course_edited_error") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastSuccessCourseRemoved" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("course_deleted_success") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastErrorCourseRemoved" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("course_deleted_error") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastErrorAddUserToCourse" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("add_user_to_course_error") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastAllAccountsCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body"><span v-html="$t('all_accounts_created')"></span></div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastXAccountsCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i18n-t keypath="x_accounts_created" tag="span">
              <b>{{ state.xAccountsCreated }}</b>
            </i18n-t>
          </div>
        </div>
      </div>

      <div class="toast text-bg-danger" id="toastErrorAccountsCreated" role="alert" aria-live="assertive"
        aria-atomic="true" data-bs-autohide="false">
        <div class="toast-body">
          {{ $t("following_accounts_not_created") }}
          <br />
          <ul>
            <li v-for=" u  in  state.username_errors ">{{ u }}</li>
          </ul>
          <div class="border-top mb-1"></div>
          {{ $t("following_accounts_not_created_password_info") }}
          <br />
          <PasswordInfo></PasswordInfo>
          <div class="mt-2 pt-2 border-top">
            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="toast">
              {{ $t("close") }}
            </button>
          </div>
        </div>
      </div>

      <div class="toast text-bg-danger" id="toastErrorAccountsCreatedCourses" role="alert" aria-live="assertive"
        aria-atomic="true" data-bs-autohide="false">
        <div class="toast-body">
          {{ $t("add_users_to_courses_error") }}
          <div class="mt-2 pt-2 border-top">
            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="toast">
              {{ $t("close") }}
            </button>
          </div>
        </div>
      </div>
    </div>



    <div class="modal fade" id="removeCourseModal" tabindex="-1" aria-labelledby="removeCourseModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5">{{ $t("delete_course") }}</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>
              <i18n-t keypath="delete_course_confirm" tag="span">
                <b>{{ state.removeCourseName }}</b>
              </i18n-t>
            </p>
            {{ $t("delete_course_confirm_info") }}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button type="button" class="btn btn-primary" @click.prevent="removeCourse()">
              {{ $t("delete_course") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="addCoursesModal" tabindex="-1" aria-labelledby="addCourseModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5">{{ $t("create_new_course") }}</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3 row">
              <label for="addCoursename" class="col-sm-4 col-form-label">{{ $t("course_name") }}</label>
              <div class="col-sm-8">
                <input type="text" class="form-control" id="addCoursename" :placeholder="$t('course_name')"
                  v-model="state.newCourseName" />
              </div>
            </div>
            <div class="mb-3 row">
              <label for="coursebackgroundcolor" class="col-sm-4 col-form-label">{{ $t("background_color") }}</label>
              <div class="col-sm-8">
                <input type="color" class="form-control form-control-color" id="coursebackgroundcolor"
                  v-model="state.newCourseColor" :title="$t('choose_color')" />
              </div>
            </div>

            <hr />

            <div class="mb-3 row">
              <label for="coursepreview" class="col-sm-4 col-form-label"><b>{{ $t("preview") }}</b></label>
              <div class="col-sm-2" style="margin-top: auto; margin-bottom: auto">
                <CourseBadge :color="state.newCourseColor" :font-dark="newCourseFontDark" :name="state.newCourseName" />
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                {{ $t("abort") }}
              </button>
              <button type="button" class="btn btn-primary" @click.prevent="addNewCourse()"
                :disabled="state.newCourseName.length < 2 || state.newCourseName.length > 30">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
                  v-if="state.courseLoading"></span>
                {{ $t("create_new_course") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editCourseModal" tabindex="-1" aria-labelledby="editCourseModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              <i18n-t keypath="edit_course_x" tag="span">
                <b>{{ state.oldCourseName }}</b>
              </i18n-t>
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3 row">
              <label for="coursename" class="col-sm-4 col-form-label">{{ $t("course_name") }}</label>
              <div class="col-sm-8">
                <input type="text" class="form-control" id="coursename" :placeholder="$t('course_name')"
                  v-model="state.editCourseName" />
              </div>
            </div>
            <div class="mb-3 row">
              <label for="coursebackgroundcolor" class="col-sm-4 col-form-label">{{ $t("background_color") }}</label>
              <div class="col-sm-8">
                <input type="color" class="form-control form-control-color" id="coursebackgroundcolor"
                  v-model="state.editCourseColor" :title="$t('choose_color')" />
              </div>
            </div>

            <hr />

            <div class="mb-3 row">
              <label for="coursepreview" class="col-sm-4 col-form-label"><b>{{ $t("preview") }}</b></label>
              <div class="col-sm-2" style="margin-top: auto; margin-bottom: auto">
                <CourseBadge :color="state.editCourseColor" :font-dark="editCourseFontDark"
                  :name="state.editCourseName" />
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                {{ $t("abort") }}
              </button>
              <button type="button" class="btn btn-primary" @click.prevent="editCourse()"
                :disabled="state.editCourseName.length < 2 || state.editCourseName > 30">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
                  v-if="state.courseLoading"></span>
                {{ $t("save_changes") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="changeUserPasswordModal" tabindex="-1" aria-labelledby="changeUserPasswordModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5">{{ $t("change_password") }}</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <h4>
              {{ state.changePasswordFullname }} ({{
                state.changePasswordUsername
              }})
            </h4>

            <form @submit.prevent="changePassword()">
              <PasswordInput v-model="state.newPassword" :description="$t('new_password')" />
            </form>

            <PasswordInfo />


            <div v-if="showChangePasswordTooShort" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("password_at_least_8") }}
            </div>

            <div v-if="state.showPasswordInvalid" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("password_doesnt_fullfill_requirements") }}
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                {{ $t("abort") }}
              </button>
              <button type="button" class="btn btn-primary" @click.prevent="changePassword()" :disabled="state.changePasswordLoading || state.newPassword.length < 8
                ">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
                  v-if="state.changePasswordLoading"></span>
                {{ $t("save_new_password") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="DeleteUserModal" tabindex="-1" aria-labelledby="deleteUserdModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5">{{ $t("delete_user") }}</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <h4>
              <i18n-t keypath="delete_pupil_or_teacher_confirm" tag="span">
                <u v-if="state.deleteUserIsTeacher">{{ $t("teacher") }}</u><u v-else>{{ $t("pupil") }}</u>
              </i18n-t>
              <br />
              <b>{{ state.deleteUserFullname }} ({{
                state.deleteUserUsername
              }})</b>
            </h4>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button type="button" class="btn btn-primary" @click.prevent="deleteUser()">
              {{ $t("delete_user") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="confirmPasswordModal" data-bs-backdrop="static" tabindex="-1"
      aria-labelledby="confirmPasswordModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            {{ $t("confirm_password") }}
          </div>
          <div class="modal-body">
            <form @submit.prevent="confirmPassword()">
              <PasswordInput v-model="state.confirmPassword" :description="$t('password')" />
            </form>
            <div v-if="state.confirmPasswordInvalid" class="alert alert-danger">
              {{ $t("password_invalid") }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click.prevent="$router.back()" data-bs-dismiss="modal">
              {{ $t("back") }}
            </button>
            <button :disabled="!state.confirmPassword.length || state.isConfirmingPassword" type="button"
              class="btn btn-primary" @click.prevent="confirmPassword()">
              <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
                v-if="state.isConfirmingPassword"></span>
              <span v-else>{{ $t("continue") }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="addPupilsModal" data-bs-backdrop="static" tabindex="-1"
      aria-labelledby="addPupilsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-scrollable modal-xl">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="addPupilsModalLabel">
              {{ $t("create_pupil_accounts") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="container">
              <PasswordInfo />

              <div class="d-flex flex-row align-items-center my-2">
                <label for="useUnifiedPassword">{{ $t("same_password_for_all_accounts") }}</label>
                <div class="mx-2 form-switch form-check">
                  <input class="form-check-input" type="checkbox" role="switch" id="useUnifiedPassword"
                    v-model="state.useUnifiedPassword" checked />
                </div>
                <div class="flex-fill form-floating"
                  :style="{ visibility: state.useUnifiedPassword ? 'visible' : 'hidden' }">
                  <input v-model="state.unifiedPassword" type="text" class="form-control" placeholder=""
                    id="unifiedPasswordLabel" />
                  <label for="unifiedPasswordLabel">{{ $t("same_password_for_all_accounts") }}</label>
                </div>
              </div>
            </div>

            <div class="row mb-3" v-for="(   pupil, index   ) in    newPupils   " :key="index">
              <div class="form-group col-md-1 text-center">
                <label></label>
                <div>
                  <span v-if="pupil.fullname != '' || pupil.username != ''">{{
                    index + 1
                  }}</span>&nbsp;
                  <font-awesome-layers v-if="pupil.fullname.trim() !== '' &&
                      pupil.username.trim() !== '' &&
                      ((!state.useUnifiedPassword &&
                        pupil.password.length >= 8) ||
                        (state.useUnifiedPassword &&
                          state.unifiedPassword.length >= 8))
                      ">
                    <font-awesome-icon icon="fa-circle" style="color: var(--bs-success)" />
                    <font-awesome-icon icon="fa-check" transform="shrink-5" style="color: white" />
                  </font-awesome-layers>
                </div>
              </div>
              <div class="col">
                <div class="form-floating">
                  <input v-model="pupil.fullname" :id="'fullname_' + index" type="text" class="form-control"
                    placeholder="" />
                  <label :for="'fullname_' + index">{{ $t("full_name") }}</label>
                </div>
              </div>
              <div class="col">
                <div class="form-floating">
                  <input v-model="pupil.username" type="text" class="form-control" placeholder=""
                    :id="'username_' + index" />
                  <label :for="'username_' + index">{{ $t("username") }}</label>
                </div>
              </div>
              <div class="col">
                <div class="form-floating" v-if="!state.useUnifiedPassword">
                  <input v-model="pupil.password" type="text" class="form-control" placeholder=""
                    :id="'password_' + index" />
                  <label :for="'password_' + index">{{ $t("password") }}</label>
                </div>
              </div>
            </div>
            <div v-if="state.showUnifiedPasswordMissing" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("no_uniform_password_set") }}
              <button type="button" class="btn-close" aria-label="Close"
                @click.prevent="state.showUnifiedPasswordMissing = false"></button>
            </div>
            <div v-if="state.showUniquePasswordMissing" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("unique_passwords_are_missing") }}
              <button type="button" class="btn-close" aria-label="Close"
                @click.prevent="state.showUniquePasswordMissing = false"></button>
            </div>
            <div v-if="state.showPasswordTooShort" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("password_at_least_8") }}
              <button type="button" class="btn-close" aria-label="Close"
                @click.prevent="state.showPasswordTooShort = false"></button>
            </div>
            <div v-if="state.showUsernameWhitespaceWarning" class="alert alert-danger alert-dismissible" role="alert">
              {{ $t("whitespace_in_username_not_allowed") }}
              <button type="button" class="btn-close" aria-label="Close"
                @click.prevent="state.showUsernameWhitespaceWarning = false"></button>
            </div>
          </div>

          <div class="alert alert-info text-center" role="alert">
            <i18n-t keypath="only_those_lines_accepted">
              <span><font-awesome-layers>
                  <font-awesome-icon icon="fa-circle" style="color: var(--bs-success)" />
                  <font-awesome-icon icon="fa-check" transform="shrink-5" style="color: white" />
                </font-awesome-layers></span>
            </i18n-t>
          </div>

          <div class="container">
            <div class="d-flex flex-row align-items-center mb-2">
              <label class="me-2" for="">
                <span v-html="$t('directly_add_pupils_to_courses')"></span>
              </label>

              <CourseBadge v-for="   c    in    state.newPupilsToCourses   " :color="c.color" :font-dark="c.fontDark"
                :name="c.name" :is-deletable="true" @remove="removeCourseFromNewPupils(c.id)" />
              <div class="btn-group">
                <a class="btn-round btn" data-bs-toggle="dropdown">
                  <font-awesome-layers class="fa-lg">
                    <font-awesome-icon icon="fa-circle" style="color: var(--bs-secondary)" />
                    <div style="color: var(--bs-light)">
                      <font-awesome-icon icon="fa-plus" transform="shrink-6" />
                    </div>
                  </font-awesome-layers>
                </a>
                <ul class="dropdown-menu">
                  <li v-for="   c    in    allCourses   ">
                    <a class="dropdown-item btn" @click.prevent="addCourseToNewPupils(c.id)">
                      <CourseBadge :color="c.color" :font-dark="c.fontDark" :name="c.name" />
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button type="button" class="btn btn-primary" @click.prevent="createPupilAccounts()"
              :disabled="state.addNewPupilsLoading">
              <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
                v-if="state.addNewPupilsLoading"></span>
              {{ $t("create_accounts") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <h1 class="text-center">{{ $t("usermanagement") }}</h1>
    <div class="btn-group non-flex text-center m-4" role="group">
      <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCoursesModal"
        @click="prepareAddCoursesModal()">
        {{ $t("create_courses") }}
        <font-awesome-icon icon="fa-solid fa-users" />
      </button>
      <button type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addPupilsModal"
        @click="preparePupilModal()">
        <font-awesome-icon icon="fa-solid fa-user-plus" /> {{ $t("create_pupil_accounts") }}
      </button>
    </div>

    <div class="container">
      <div class="row mb-4 ms-1">
        {{ $t("courses") }}:
        <div class="col">
          <CourseBadge v-for="   c    in    allCourses   " :color="c.color" :font-dark="c.fontDark" :name="c.name"
            :is-deletable="true" :is-editable="true" @remove="openModalRemoveCourse(c.id)"
            @edit="openModalEditCourse(c.id)" />
        </div>
      </div>
      <div class="row">
        <div class="col-3">
          <div class="input-group mb-3">
            <span class="round-left input-group-text" id="basic-addon1">
              <font-awesome-icon icon="fa-solid fa-user" /></span>
            <div class="form-floating">
              <input type="text" id="floatingInputSearchPerson" class="form-control round-right"
                v-model="state.searchName" placeholder="" />
              <label for="floatingInputSearchPerson">{{ $t("search_users") }}</label>
            </div>
          </div>
        </div>
      </div>

      <table class="table table-striped table-hover align-middle">
        <thead>
          <tr>
            <th scope="col">{{ $t("database_id") }}</th>
            <th scope="col">{{ $t("name") }}</th>
            <th scope="col">{{ $t("username") }}</th>
            <th scope="col">{{ $t("courses") }}</th>
            <th scope="col">{{ $t("role") }}</th>
            <th scope="col">{{ $t("settings") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr class="py-1" v-for="   x    in    allUsersFilteredSorted   " @mouseover="selectUser(x)"
            @mouseleave="unselectUser()">
            <th scope="row">{{ x.id }}</th>
            <td>
              <div v-if="!(state.edit_user_id == x.id && state.edit_user_property === 'name')">{{ x.full_name
              }} <a style="cursor: pointer" @click.prevent="edit_user(x.id, 'name', x.full_name)"
                  :class="{ invisible: x != state.selectedUser }"><font-awesome-icon style="color: var(--bs-secondary);"
                    icon="fa-solid fa-pencil" /></a></div>
              <!-- edit-area -->
              <div v-else class="col-auto">
                <input class="form-control w-auto d-inline" type="text" v-model="state.edited_name">
                <a v-if="!state.changingName" class="mx-2" @click.prevent="change_name(x.id)"
                  style="color: green; cursor: pointer;">
                  <font-awesome-icon icon="fa-check" />
                </a>
                <a v-if="!state.changingName" @click.prevent="abort_edit_user()" style="color: red; cursor: pointer;">
                  <font-awesome-icon icon="fa-xmark" />
                </a>
                <div v-if="state.changingName" class="spinner-border" role="status">
                  <span class="visually-hidden"></span>
                </div>
              </div>
            </td>
            <td>
              <div v-if="!(state.edit_user_id == x.id && state.edit_user_property === 'username')">{{ x.username
              }} <a style="cursor: pointer" @click.prevent="edit_user(x.id, 'username', x.username)"
                  :class="{ invisible: x != state.selectedUser }"><font-awesome-icon style="color: var(--bs-secondary);"
                    icon="fa-solid fa-pencil" /></a></div>
              <!-- edit-area -->
              <div v-else class="col-auto">
                <input class="form-control w-auto d-inline" type="text" v-model="state.edited_username">
                <a v-if="!state.changingUsername" class="mx-2" @click.prevent="change_username(x.id)"
                  style="color: green; cursor: pointer;">
                  <font-awesome-icon icon="fa-check" />
                </a>
                <a v-if="!state.changingUsername" @click.prevent="abort_edit_user()" style="color: red; cursor: pointer;">
                  <font-awesome-icon icon="fa-xmark" />
                </a>
                <div v-if="state.changingUsername" class="spinner-border" role="status">
                  <span class="visually-hidden"></span>
                </div>
              </div>
            </td>
            <td>
              <CourseBadge v-for="   c    in    x.courses   " :color="c.color" :font-dark="c.fontDark" :name="c.name"
                :is-deletable="true" @remove="removeCourseFromUser(x.id, c.id)" />
              <div class="btn-group" v-if="x.role === 'pupil'">
                <a class="btn-round btn" data-bs-toggle="dropdown">
                  <font-awesome-layers class="fa-lg">
                    <font-awesome-icon icon="fa-circle" style="color: var(--bs-secondary)" />
                    <div style="color: var(--bs-light)">
                      <font-awesome-icon icon="fa-plus" transform="shrink-6" />
                    </div>
                  </font-awesome-layers>
                </a>
                <ul class="dropdown-menu courseDropdown" data-bs-theme="light">
                  <li v-for="   c    in    allCourses   ">
                    <a class="dropdown-item btn" @click.prevent="addCourseToUser(x.id, c.name)">
                      <CourseBadge :color="c.color" :font-dark="c.fontDark" :name="c.name" />
                    </a>
                  </li>
                </ul>
              </div>
            </td>
            <td><span v-if="x.role === 'teacher'">👨‍🏫</span> {{ x.role }}</td>
            <td>
              <a class="btn-round btn" data-bs-toggle="modal" data-bs-target="#changeUserPasswordModal"
                @click.prevent="openModalChangePassword(x.id)">
                <font-awesome-layers class="fa-lg">
                  <font-awesome-icon icon="fa-circle" style="color: var(--bs-warning)" />
                  <div style="color: black">
                    <font-awesome-icon icon="fa-key" transform="shrink-6" />
                  </div>
                </font-awesome-layers>
              </a>
              <a class="btn-round btn ps-3" data-bs-toggle="modal" data-bs-target="#DeleteUserModal"
                @click.prevent="openModalDeleteUser(x.id)">
                <font-awesome-layers class="fa-lg">
                  <font-awesome-icon icon="fa-circle" style="color: var(--bs-danger)" />
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
  </div>
</template>

<style scoped lang="scss">
.dropdown-menu {
  min-width: 0;
}

.greyButton {
  text-decoration: none;
  color: inherit;
}

.invisible {
  visibility: hidden;
}


.round-left {
  border-top-left-radius: var(--bs-border-radius-pill);
  border-bottom-left-radius: var(--bs-border-radius-pill);
}

.round-right {
  border-top-right-radius: var(--bs-border-radius-pill);
  border-bottom-right-radius: var(--bs-border-radius-pill);
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
