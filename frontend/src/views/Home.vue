<script setup>
import { computed, onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue";
import { useAuthStore } from "../stores/auth.store.js";
import { useRouter } from "vue-router";
import { Toast, Modal } from "bootstrap";
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useI18n } from 'vue-i18n'
import CourseBadge from "../components/CourseBadge.vue";

const i18n = useI18n()

const router = useRouter();

const authStore = useAuthStore();

let state = reactive({
  myProjects: [],
  new_homework: [],
  old_homework: [],
  projectToDelete: null,
  renameUuid: "",
  renameId: 0,
  renameName: "",
  renameNameNew: "",
  isRenaming: false,
  isDeleting: false,
  searchProject: "",
  addSolutionHomeworkId: 0,
  solution_id: 0,
  solution_start_showing: new Date(),
  isAddingSolution: false,
  addSolutionInputInvalid: false,
  deleteSolutionHomeworkId: 0,
  isDeletingSolution: false,
  coursesInHomework: [],
  filter_course_id: null,
});

onBeforeMount(() => {
  if (authStore.isTeacher()) {
    getProjectsAsTeacher();
  } else {
    getProjectsAsPupil();
  }

  document.title = i18n.t("home_title");
});

function filterForSearchString(array, searchstring) {

  return array.filter((project) => {
    // filter for selected courses as teacher
    if (state.filter_course_id !== null && project.course_id !== undefined && project.course_id != state.filter_course_id) {
      return false;
    }

    if (!searchstring.length) return true;

    return (
      project.name.toLowerCase().includes(searchstring.toLowerCase()) ||
      project.description
        .toLowerCase()
        .includes(searchstring.toLowerCase())
    );
  });
}

const myProjectsFiltered = computed(() => {
  let arr = filterForSearchString(state.myProjects, state.searchProject)
  return arr.reverse()
});

const newHomeworkFiltered = computed(() => {
  let arr = filterForSearchString(state.new_homework, state.searchProject)
  return arr.reverse()
});

const oldHomeworkFiltered = computed(() => {
  let arr = filterForSearchString(state.old_homework, state.searchProject)
  return arr.reverse()
});

function getCoursesOutOfHomework(homework) {
  homework.forEach((h) => {
    let found = false
    for (let i = 0; i < state.coursesInHomework.length; i++) {
      if (state.coursesInHomework[i].id == h.course_id) {
        found = true
        break
      }
    }
    if (!found) {
      state.coursesInHomework.push({
        id: h.course_id,
        name: h.course_name,
        color: h.course_color,
        fontDark: h.course_font_dark
      })
    }
  })
}

function getProjectsAsTeacher() {
  CodeService.getProjectsAsTeacher().then(
    (response) => {
      state.myProjects = response.data.projects;
      state.new_homework = [];
      state.old_homework = [];

      getCoursesOutOfHomework(response.data.homework)

      response.data.homework.forEach((h) => {
        if (new Date(h.deadline) > new Date()) {
          state.new_homework.push(h);
        } else {
          state.old_homework.push(h);
        }
      });
    },
    (error) => {
      if (error.response) {
        console.log(error.response);
      }
    }
  );
}

function getProjectsAsPupil() {
  CodeService.getProjectsAsPupil().then(
    (response) => {
      state.myProjects = response.data.projects;
      state.new_homework = [];
      state.old_homework = [];

      response.data.homework.forEach((h) => {
        if (new Date(h.deadline) > new Date()) {
          state.new_homework.push(h);
        } else {
          state.old_homework.push(h);
        }
      });
    },
    (error) => {
      if (error.response) {
        console.log(error.response);
      }
    }
  );
}

function startHomework(id) {
  CodeService.startHomework(id).then(
    (response) => {
      if (response.data.success) {
        router.push({
          name: "ide",
          params: {
            project_uuid: response.data.uuid,
            user_id: response.data.branch,
          },
        });
      }
    },
    (error) => {
      console.log(error.response);
      const toast = new Toast(
        document.getElementById("toastStartHomeworkError")
      );
      toast.show();
    }
  );
}

function askDeleteHomework(id, name) {
  state.deleteId = id;
  state.deleteName = name;
  const modal = new Modal(document.getElementById("deleteHomeworkModal"));
  modal.show();
}

function askDeleteHomeworkBranch(uuid, user_id, name) {
  state.deleteUuid = uuid;
  state.deleteUserId = user_id;
  state.deleteName = name;
  const modal = new Modal(document.getElementById("deleteHomeworkBranchModal"));
  modal.show();
}

function askDeleteProject(uuid, user_id, name) {
  state.deleteUuid = uuid;
  state.deleteUserId = user_id;
  state.deleteName = name;
  if (user_id === undefined) {
    const modal = new Modal(document.getElementById("deleteProjectModal"));
    modal.show();
  } else {
    const modal = new Modal(
      document.getElementById("deleteHomeworkBranchModal")
    );
    modal.show();
  }
}

function deleteProject(uuid, user_id) {
  if (user_id === undefined) user_id = 0;

  //show modal which asks if the user really wants to delete the project

  CodeService.deleteProject(uuid, user_id).then(
    (response) => {
      if (response.data) {
        state.myProjects = state.myProjects.filter((p) => p.uuid != uuid);
        if (user_id != 0) {
          getProjectsAsPupil();
        } else {
          getProjectsAsTeacher();
        }

        const toast = new Toast(
          document.getElementById("toastDeleteProjectSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteProjectError")
        );
        toast.show();
      }
    },
    (error) => {
      console.log(error.response);
    }
  );
}

function deleteHomework(id) {
  CodeService.deleteHomework(id).then(
    (response) => {
      if (response.data) {
        state.new_homework = state.new_homework.filter((p) => p.id != id);
        state.old_homework = state.old_homework.filter((p) => p.id != id);

        const toast = new Toast(
          document.getElementById("toastDeleteProjectSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteProjectError")
        );
        toast.show();
      }
    },
    (error) => {
      console.log(error.response);
    }
  );
}

function askRenameHomework(id, name) {
  state.renameId = id;
  state.renameName = name;
  state.renameNameNew = name;

  const modal = new Modal(document.getElementById("renameHomeworkModal"));
  modal.show();

  document.getElementById('renameHomeworkModal').addEventListener('shown.bs.modal', function () {
    document.getElementById("renameHomeworknameInput").focus();
  })
}

function renameHomework() {
  state.isRenaming = true;

  CodeService.renameHomework(state.renameId, state.renameNameNew).then(
    (response) => {
      state.isRenaming = false;

      // close modal
      var elem = document.getElementById("renameHomeworkModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        // update name in list
        state.new_homework.forEach((h) => {
          if (h.id == state.renameId) {
            h.name = state.renameNameNew;
          }
        });
        state.old_homework.forEach((h) => {
          if (h.id == state.renameId) {
            h.name = state.renameNameNew;
          }
        });

        const toast = new Toast(
          document.getElementById("toastRenameHomeworkSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastRenameHomeworkError")
        );
        toast.show();
      }
    },
    (error) => {
      // close modal
      var elem = document.getElementById("renameHomeworkModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      state.isRenaming = false;
      console.log(error.response);
    }
  );
}

function askRenameProject(uuid, name) {
  state.renameUuid = uuid;
  state.renameName = name;
  state.renameNameNew = name;

  const modal = new Modal(document.getElementById("renameProjectModal"));
  modal.show();

  document.getElementById('renameProjectModal').addEventListener('shown.bs.modal', function () {
    document.getElementById("renameProjectnameInput").focus();
  })
}

function renameProject() {
  state.isRenaming = true;

  CodeService.renameProject(state.renameUuid, state.renameNameNew).then(
    (response) => {
      state.isRenaming = false;

      // close modal
      var elem = document.getElementById("renameProjectModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        // update name in list
        state.myProjects.forEach((p) => {
          if (p.uuid == state.renameUuid) {
            p.name = state.renameNameNew;
          }
        });

        const toast = new Toast(
          document.getElementById("toastRenameProjectSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastRenameProjectError")
        );
        toast.show();
      }
    },
    (error) => {
      // close modal
      var elem = document.getElementById("renameProjectModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      state.isRenaming = false;
      console.log(error.response);
    }
  );
}

function duplicateProject(uuid) {
  state.isDuplicating = true;

  CodeService.duplicateProject(uuid).then(
    (response) => {
      state.isDuplicating = false;
      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastDuplicateProjectSuccess")
        );
        toast.show();

        // reload all projects
        if (authStore.isTeacher()) {
          getProjectsAsTeacher();
        } else {
          getProjectsAsPupil();
        }
      } else {
        const toast = new Toast(
          document.getElementById("toastDuplicateProjectError")
        );
        toast.show();
      }
    },
    (error) => {
      state.isDuplicating = false;
      console.log(error.response);
    }
  );
}

/* 🛑 This function also exists at ../IDE.vue 🛑 */
function downloadProject(uuid) {
  CodeService.downloadProject(uuid).then(
    (response) => {
      console.log(response.headers["content-disposition"]);
      let filename =
        response.headers["content-disposition"].split("filename=")[1];

      let fileUrl = window.URL.createObjectURL(response.data);
      let fileLink = document.createElement("a");

      fileLink.href = fileUrl;
      fileLink.setAttribute("download", filename);
      document.body.appendChild(fileLink);

      fileLink.click();

      // remove link from DOM
      document.body.removeChild(fileLink);
    },
    (error) => {
      console.log(error.response);
      const toast = new Toast(
        document.getElementById("toastDownloadProjectError")
      );
      toast.show();
    }
  );
}

function openAddSolutionModal(homework_id) {
  if (!authStore.isTeacher()) {
    return
  }
  state.addSolutionHomeworkId = homework_id
  state.addSolutionInputInvalid = false


  // get solution_id from homework_id
  let found = false
  for (var i = 0; i < state.old_homework.length; i++) {
    if (state.old_homework[i].id == homework_id) {
      state.solution_id = state.old_homework[i].solution_id
      state.solution_start_showing = state.old_homework[i].solution_start_showing
      found = true
      break
    }
  }
  if (!found) {
    for (var i = 0; i < state.new_homework.length; i++) {
      if (state.new_homework[i].id == homework_id) {
        state.solution_id = state.new_homework[i].solution_id
        state.solution_start_showing = state.new_homework[i].solution_start_showing
        break
      }
    }
  }

  if (state.solution_id == 0) {
    state.solution_id = null
  }

  const modal = new Modal(document.getElementById("editSolutionModal"));
  modal.show();
}

function openDeleteSolutionModal(homework_id) {
  if (!authStore.isTeacher()) {
    return
  }
  state.deleteSolutionHomeworkId = homework_id

  const modal = new Modal(document.getElementById("deleteSolutionModal"));
  modal.show();
}

function deleteSolution() {
  if (!authStore.isTeacher() || state.isDeletingSolution) {
    return
  }

  if (state.deleteSolutionHomeworkId === null || state.deleteSolutionHomeworkId === 0) {
    //show error
    const toast = new Toast(
      document.getElementById("toastDeleteSolutionError")
    );
    toast.show();

    //close modal
    var elem = document.getElementById("deleteSolutionModal");
    var modal = Modal.getInstance(elem);
    modal.hide();

    return
  }

  state.isDeletingSolution = true

  CodeService.deleteSolution(state.deleteSolutionHomeworkId).then(
    (response) => {
      state.isDeletingSolution = false

      //close modal
      var elem = document.getElementById("deleteSolutionModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        getProjectsAsTeacher();

        const toast = new Toast(
          document.getElementById("toastDeleteSolutionSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastDeleteSolutionError")
        );
        toast.show();
      }
    },
    (error) => {
      state.isDeletingSolution = false
      console.log(error.response);

      //close modal
      var elem = document.getElementById("deleteSolutionModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastDeleteSolutionError")
      );
      toast.show();
    }
  )

}

function addSolution() {
  if (!authStore.isTeacher()) {
    return
  }

  if (state.solution_id === null || state.solution_id === 0) {
    state.addSolutionInputInvalid = true;
    return
  }

  state.isAddingSolution = true;

  CodeService.addSolution(state.addSolutionHomeworkId, state.solution_id, state.solution_start_showing).then(
    (response) => {
      state.isAddingSolution = false;

      // close modal
      var elem = document.getElementById("editSolutionModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        getProjectsAsTeacher();

        const toast = new Toast(
          document.getElementById("toastAddSolutionSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastAddSolutionError")
        );
        toast.show();
      }
    },
    (error) => {
      state.addSolutionInputInvalid = true;
      state.isAddingSolution = false;
      console.log(error.response);
    }
  );

}

function collapseNewHomework() {
  const newHomeworkHeader = document.getElementById("newHomeworkHeader");
  const arrowNewHomework = document.getElementById("arrowNewHomework");
  if (newHomeworkHeader.classList.contains("collapsed")) {
    arrowNewHomework.classList.remove("arrowDown");
  } else {
    arrowNewHomework.classList.add("arrowDown");
  }
}

function collapseOldHomework() {
  const oldHomeworkHeader = document.getElementById("oldHomeworkHeader");
  const arrowOldHomework = document.getElementById("arrowOldHomework");
  if (oldHomeworkHeader.classList.contains("collapsed")) {
    arrowOldHomework.classList.remove("arrowDown");
  } else {
    arrowOldHomework.classList.add("arrowDown");
  }
}

function collapseMyProjects() {
  const myProjectsHeader = document.getElementById("myProjectsHeader");
  const arrowMyProjects = document.getElementById("arrowMyProjects");
  if (myProjectsHeader.classList.contains("collapsed")) {
    arrowMyProjects.classList.remove("arrowDown");
  } else {
    arrowMyProjects.classList.add("arrowDown");
  }
}

</script>

<template>
  <div>
    <!-- Toasts -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastStartHomeworkError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastStartHomeworkError") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteSolutionError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastDeleteSolutionError") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDeleteSolutionSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastDeleteSolutionSuccess") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastAddSolutionSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastAddSolutionSuccess") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastAddSolutionError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastAddSolutionError") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDownloadProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastDownloadProjectError") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDuplicateProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastDuplicateProjectSuccess") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDuplicateProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastDuplicateProjectError") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastRenameHomeworkSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastRenameHomeworkSuccess") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastRenameHomeworkError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastRenameHomeworkError") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastRenameProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastRenameProjectSuccess") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastRenameProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">{{ $t("toastRenameProjectError") }}</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastDeleteProjectError") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDeleteProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("toastDeleteProjectSuccess") }}
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div class="modal fade" id="renameHomeworkModal" tabindex="-1" aria-labelledby="renameHomeworkModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("rename_assignment") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <i18n-t keypath="enter_new_assignment_name" tag="label">
              <b>{{ state.renameName }}</b>
            </i18n-t>
            <div class="input-group mt-3">
              <input type="text" class="form-control" id="renameHomeworknameInput" :placeholder="state.renameName"
                v-model="state.renameNameNew" @keyup.enter="renameHomework()" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button :disabled="state.renameNameNew.trim() === ''" @click.prevent="renameHomework()" type="button"
              class="btn btn-primary">
              <span v-if="!state.isRenaming"> {{ $t("rename") }} </span>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="renameProjectModal" tabindex="-1" aria-labelledby="renameProjectModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("rename_project") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <i18n-t keypath="enter_new_project_name" tag="label">
              <b>{{ state.renameName }}</b>
            </i18n-t>
            <div class="input-group mt-3">
              <input type="text" class="form-control" id="renameProjectnameInput" :placeholder="state.renameName"
                v-model="state.renameNameNew" @keyup.enter="renameProject()" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button :disabled="state.renameNameNew.trim() === ''" @click.prevent="renameProject()" type="button"
              class="btn btn-primary">
              <span v-if="!state.isRenaming"> {{ $t("rename") }} </span>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteProjectModal" tabindex="-1" aria-labelledby="deleteProjectModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("delete_private_project") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <i18n-t keypath="want_to_delete_private_project" tag="label">
              <b>{{ state.deleteName }}</b>
            </i18n-t>

            <div v-if="authStore.isTeacher()" class="mt-3 alert alert-warning">
              {{ $t("delete_private_project_teacher_warning") }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button @click.prevent="
              deleteProject(state.deleteUuid, state.deleteUserId)
              " type="button" class="btn btn-primary" data-bs-dismiss="modal">
              {{ $t("delete") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteHomeworkBranchModal" tabindex="-1" aria-labelledby="deleteHomeworkBranchModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("delete_progress") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <i18n-t keypath="want_to_delete_progress" tag="label">
              <br>
              <br>
              <b>{{ state.deleteName }}</b>
            </i18n-t>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button @click.prevent="
              deleteProject(state.deleteUuid, state.deleteUserId)
              " type="button" class="btn btn-primary" data-bs-dismiss="modal">
              {{ $t("delete") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteHomeworkModal" tabindex="-1" aria-labelledby="deleteHomeworkModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("delete_assignment") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <i18n-t keypath="want_to_delete_assignment" tag="label">
              <b>{{ state.deleteName }}</b>
            </i18n-t>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button @click.prevent="deleteHomework(state.deleteId)" type="button" class="btn btn-primary"
              data-bs-dismiss="modal">
              {{ $t("delete") }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editSolutionModal" tabindex="-1" aria-labelledby="editSolutionModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              <span>{{ $t("add_solution") }}</span>
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              {{ $t("add_solution_info") }}
            </div>
            <label class="form-label">{{ $t("select_the_solution") }}</label>
            <v-select :options="state.myProjects" v-model="state.solution_id" label="name" :reduce="p => p.id"
              placeholder="">
            </v-select>
            <br>
            <br>
            <label class="form-label">{{ $t("solution_visible_from_when") }}</label>
            <div class="d-flex flex-row align-items-center">
              <button type="button" class="btn btn-primary btn-sm"
                @click.prevent="state.solution_start_showing = new Date()">
                {{ $t("from_right_now") }}
              </button>
              <span class="mx-2"><b>{{ $t("or") }}</b></span>
              <VueDatePicker class="flex-fill" v-model="state.solution_start_showing" :placeholder="$t('select_date')"
                text-input auto-apply prevent-min-max-navigation :locale="$t('locale')"
                :format="$t('long_date_format')" />
            </div>
            <font-awesome-icon icon="fa-solid fa-arrow-right" fixed-width />
            <span v-if="state.solution_start_showing === '' || state.solution_start_showing == null">
              <em class="text-bg-warning">{{ $t("input_missing") }}</em>
            </span>
            <span v-else-if="(new Date(state.solution_start_showing) <= new Date())">
              <b v-html="$t('visible_from_now')">
              </b>
            </span>
            <span v-else><b>
                <i18n-t keypath="visible_in_x_days_hours" tag="label">
                  <u>{{ $t("visible_in_x_days", Math.floor((new Date(state.solution_start_showing)
                    -
                    new
                      Date()) / (1000 * 3600 * 24))) }}
                  </u>
                  <u>
                    {{
                      $t("visible_in_x_hours", Math.floor((new Date(state.solution_start_showing) - new Date()) / (1000
                        * 3600) % 24)) }}
                  </u>
                </i18n-t>
              </b>
            </span>
            <br>

            <div v-if="state.addSolutionInputInvalid" class="alert alert-danger mt-4">
              {{ $t("add_solution_input_invalid") }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button @click.prevent="addSolution()" type="button" class="btn btn-primary" :disabled="!state.solution_id">
              <div v-if="!state.isAddingSolution">{{ $t("save") }}</div>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="deleteSolutionModal" tabindex="-1" aria-labelledby="deleteSolutionModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              {{ $t("delete_solution") }}
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            {{ $t("delete_solution_confirm") }}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ $t("abort") }}
            </button>
            <button @click.prevent="deleteSolution()" type="button" class="btn btn-primary">
              <div v-if="state.isDeletingSolution" class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <div v-else>
                {{ $t("delete") }}
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container main">
      <div class="d-flex flex-row flex-wrap align-items-center justify-content-center headrow">
        <div class="flex-div">
          <a class="btn btn-outline-success my-3 sticky-content " type="submit" href="/#/newProject">
            {{ $t("new_project") }} <font-awesome-icon icon="fa-solid fa-plus" />
          </a>
        </div>
        <div class="flex-div">
          <div class="input-group searchProject">
            <span class="round-left input-group-text" id="basic-addon1">
              <font-awesome-icon icon="fa-solid fa-search" /></span>
            <div class="form-floating">
              <input type="text" id="floatingInputSearchProject" class="form-control" v-model="state.searchProject"
                placeholder="" />
              <label for="floatingInputSearchProject">{{ $t("project_search") }}</label>
            </div>
            <span :class="{ grey: !state.searchProject.length }" class="round-right input-group-text resetSearchProject"
              @click.prevent="state.searchProject = ''">
              <font-awesome-icon icon="fa-solid fa-xmark" />
            </span>
          </div>
        </div>
        <div class="flex-div w-100"><!-- Don't remove (necessary for middle-positioning) -->
          <div class="w-50 my-3" id="courseFilter" v-if="authStore.isTeacher()">
            <v-select :options="state.coursesInHomework" v-model="state.filter_course_id" key="name" label="name"
              :placeholder="$t('filter_courses')" :reduce="c => c.id">
              <template #option="option">
                <CourseBadge :name="option.name" :color="option.color" :fontDark="option.fontDark" />
              </template>
            </v-select>
          </div>
        </div>
      </div>

      <h2 v-if="state.new_homework.length" class="noSelect">
        <div class="fit-content" data-bs-toggle="collapse" href="#newHomework" id="newHomeworkHeader"
          @click.prevent="collapseNewHomework()">
          <div class="arrow arrowDown" id="arrowNewHomework">➤</div> {{ $t("current_assignment") }}
        </div>
      </h2>
      <div class="collapse show" id="newHomework">
        <div class="d-flex align-content-start flex-wrap cards">
          <!-- if teacher: -->
          <ProjectCard v-if="authStore.isTeacher()" v-for="( h, index ) in  newHomeworkFiltered "
            :key="`${index}-${h.id}`" isHomework isTeacher :name="h.name" :description="h.description" :id="h.id"
            :deadline="h.deadline" :courseName="h.course_name" :courseColor="h.course_color"
            :courseFontDark="h.course_font_dark" :solution_name="h.solution_name"
            :solution_start_showing="h.solution_start_showing" :solution_id="h.solution_id"
            @renameHomework="askRenameHomework" @deleteHomework="askDeleteHomework" @addSolution="openAddSolutionModal"
            @deleteSolution="openDeleteSolutionModal" :pupils_editing="h.pupils_editing"
            :pupils_in_course="h.pupils_in_course" :submission="h.submission" :enableTests="h.enable_tests" />

          <!-- else -->
          <ProjectCard v-else v-for="( h, index2 ) in  newHomeworkFiltered " :key="`${index2}-${h.id}`" isHomework
            @startHomework="startHomework" :isEditing="h.is_editing" :name="h.name" :description="h.description"
            :uuid="h.uuid" :branch="h.branch" :id="h.id" :deadline="h.deadline" :solution_uuid="h.solution_uuid"
            @deleteHomeworkBranch="askDeleteHomeworkBranch" :submission="h.submission" :enableTests="h.enable_tests" />
        </div>
      </div>

      <h2 v-if="state.old_homework.length" class="noSelect">
        <div class="fit-content" id="oldHomeworkHeader" data-bs-toggle="collapse" href="#oldHomework"
          @click.prevent="collapseOldHomework()">
          <div class="arrow arrowDown" id="arrowOldHomework">➤</div> {{ $t("previous_assignments") }}
        </div>
      </h2>
      <div class="collapse show" id="oldHomework">
        <div class="d-flex align-content-start flex-wrap cards">
          <!-- if teacher: -->
          <ProjectCard v-if="authStore.isTeacher()" v-for="( h, index ) in  oldHomeworkFiltered "
            :key="`${index}-${h.id}`" isHomework isOld isTeacher :name="h.name" :description="h.description" :id="h.id"
            :deadline="h.deadline" :courseName="h.course_name" :courseColor="h.course_color"
            :courseFontDark="h.course_font_dark" :solution_name="h.solution_name"
            :solution_start_showing="h.solution_start_showing" :solution_id="h.solution_id"
            @renameHomework="askRenameHomework" @deleteHomework="askDeleteHomework" @addSolution="openAddSolutionModal"
            @deleteSolution="openDeleteSolutionModal" :pupils_editing="h.pupils_editing"
            :pupils_in_course="h.pupils_in_course" :submission="h.submission" :enableTests="h.enable_tests" />

          <!-- else -->
          <ProjectCard v-else v-for="( h, index2 ) in  oldHomeworkFiltered " :key="`${index2}-${h.id}`" isHomework isOld
            @startHomework="startHomework" :isEditing="h.is_editing" :name="h.name" :uuid="h.uuid"
            :description="h.description" :branch="h.branch" :id="h.id" :deadline="h.deadline"
            :solution_uuid="h.solution_uuid" @deleteHomeworkBranch="askDeleteHomeworkBranch" :submission="h.submission"
            :enableTests="h.enable_tests" />
        </div>
      </div>

      <h2 v-if="state.myProjects.length" class="noSelect">
        <div class="fit-content" data-bs-toggle="collapse" href="#myProjects" id="myProjectsHeader"
          @click.prevent="collapseMyProjects()">
          <div class="arrow arrowDown" id="arrowMyProjects">➤</div> {{ $t("my_projects") }}
        </div>
        <div v-if="state.isDuplicating" class="spinner-border text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </h2>
      <div class="collapse show" id="myProjects">
        <div class="d-flex align-content-start flex-wrap cards">
          <ProjectCard v-for="( p, index ) in  myProjectsFiltered " :name="p.name" :description="p.description"
            :uuid="p.uuid" :key="`${index}-${p.uuid}`" @renameProject="askRenameProject"
            @duplicateProject="duplicateProject" @downloadProject="downloadProject" @deleteProject="askDeleteProject" />
        </div>
      </div>

      <div class="height-buffer">
      </div>
    </div>
  </div>
</template>

<style lang="scss">
[data-bs-theme=dark] {
  #courseFilter>div>div {
    border-color: gray;
  }

  #courseFilter>div>div>.vs__selected-options>span {
    color: lightgray;
  }

  #courseFilter>div>div>.vs__actions>button>svg,
  #courseFilter>div>div>.vs__actions>svg {
    fill: lightgray;
  }
}
</style>

<style scoped>
.height-buffer {
  height: 100px;
}

.fit-content {
  width: fit-content;
}

.noSelect {
  user-select: none;
}

.arrow {
  display: inline-block;
  transition: transform 0.2s;
}

.arrowDown {
  transform: rotate(90deg);
}

@media (max-width: 1199px) {
  .cards {
    justify-content: center;
  }
}

@media (max-width: 767px) {
  .headrow {
    flex-direction: column !important;
  }
}

.flex-div {
  flex: 1;
  display: flex;
  justify-content: center;
}

.flex-div:first-child>a {
  margin-right: auto;
}


.searchProject {
  width: inherit !important;
}

.round-left {
  border-top-left-radius: var(--bs-border-radius-pill);
  border-bottom-left-radius: var(--bs-border-radius-pill);
}

.round-right {
  border-top-right-radius: var(--bs-border-radius-pill);
  border-bottom-right-radius: var(--bs-border-radius-pill);
}

.resetSearchProject {
  cursor: pointer;
}

.grey {
  cursor: auto !important;
  color: grey;
}

.main {
  overflow-y: hidden;
}

.sticky-content {
  position: sticky;
  top: 0;
}

.card-text {
  white-space: pre-line;
}
</style>
