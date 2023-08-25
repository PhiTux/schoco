<script setup>
import { computed, onBeforeMount, reactive } from "vue";
import CodeService from "../services/code.service.js";
import ProjectCard from "../components/ProjectCard.vue";
import AddSolutionModalContent from "../components/AddSolutionModalContent.vue";
import { useAuthStore } from "../stores/auth.store.js";
import { useRouter } from "vue-router";
import { Toast, Modal } from "bootstrap";

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
  addSolutionHomeworkId: 0
});

onBeforeMount(() => {
  if (authStore.isTeacher()) {
    getProjectsAsTeacher();
  } else {
    getProjectsAsPupil();
  }

  document.title = "Home";
});

function filterForSearchString(array, searchstring) {
  return array.filter((project) => {
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
  return filterForSearchString(state.myProjects, state.searchProject)
});

const newHomeworkFiltered = computed(() => {
  return filterForSearchString(state.new_homework, state.searchProject)
});

const oldHomeworkFiltered = computed(() => {
  return filterForSearchString(state.old_homework, state.searchProject)
});

function getProjectsAsTeacher() {
  CodeService.getProjectsAsTeacher().then(
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

function addSolution(homework_id) {
  state.addSolutionHomeworkId = homework_id
  const modal = new Modal(document.getElementById("addSolutionModal"));
  modal.show();
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
            Fehler beim Starten der Hausaufgabe. Probiere es erneut und frage
            andernfalls deine Lehrkraft um Hilfe.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDownloadProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Fehler beim Download des Projekts.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDuplicateProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Projekt wurde dupliziert.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDuplicateProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Fehler beim Duplizieren des Projekts.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastRenameHomeworkSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Hausaufgabe wurde umbenannt.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastRenameHomeworkError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Hausaufgabe konnte nicht umbenannt werden.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastRenameProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Projekt wurde umbenannt.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastRenameProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Projekt konnte nicht umbenannt werden.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Löschen des Projekts / der Hausaufgabe.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastDeleteProjectSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Das Projekt oder die Hausaufgabe wurde erfolgreich gelöscht.
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
              Hausaufgabe umbenennen
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Gib den neuen Namen für die Hausaufgabe
            <b>{{ state.renameName }}</b> ein:
            <div class="input-group mt-3">
              <input type="text" class="form-control" id="renameHomeworknameInput" :placeholder="state.renameName"
                v-model="state.renameNameNew" @keyup.enter="renameHomework()" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button :disabled="state.renameNameNew.trim() === ''" @click.prevent="renameHomework()" type="button"
              class="btn btn-primary">
              <span v-if="!state.isRenaming"> Umbenennen </span>
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
              Projekt umbenennen
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Gib den neuen Namen für das Projekt
            <b>{{ state.renameName }}</b> ein:
            <div class="input-group mt-3">
              <input type="text" class="form-control" id="renameProjectnameInput" :placeholder="state.renameName"
                v-model="state.renameNameNew" @keyup.enter="renameProject()" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button :disabled="state.renameNameNew.trim() === ''" @click.prevent="renameProject()" type="button"
              class="btn btn-primary">
              <span v-if="!state.isRenaming"> Umbenennen </span>
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
              Privates Projekt löschen?
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Möchtest du wirklich dein eigenes, privates Projekt mit dem Titel
            <b>{{ state.deleteName }}</b>
            löschen?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button @click.prevent="
              deleteProject(state.deleteUuid, state.deleteUserId)
              " type="button" class="btn btn-primary" data-bs-dismiss="modal">
              Löschen
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
              Fortschritt löschen?
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Du kannst eine Hausaufgabe nicht völlig löschen. Du kannst nur
            deinen bisherigen Fortschritt löschen und anschließend wieder in
            einem "sauberen" Projekt von vorne beginnen.
            <br />
            <br />
            Möchtest du wirklich deinen Fortschritt von
            <b>{{ state.deleteName }}</b>
            löschen?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button @click.prevent="
              deleteProject(state.deleteUuid, state.deleteUserId)
              " type="button" class="btn btn-primary" data-bs-dismiss="modal">
              Löschen
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
              Hausaufgabe löschen?
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Wenn du eine Hausaufgabe löschst, dann wird sie auch bei allen
            Schüler/innen gelöscht. Möchtest du wirklich die Hausaufgabe mit dem
            Titel <b>{{ state.deleteName }}</b> löschen?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button @click.prevent="deleteHomework(state.deleteId)" type="button" class="btn btn-primary"
              data-bs-dismiss="modal">
              Löschen
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="addSolutionModal" tabindex="-1" aria-labelledby="addSolutionModalLabel"
      aria-hidden="true">
      <AddSolutionModalContent :homework_id="state.addSolutionHomeworkId" :my-projects="state.myProjects" />
    </div>

    <div class="container main">
      <div class="d-flex flex-row flex-wrap align-items-center justify-content-center">
        <div class="flex-div">
          <a class="btn btn-outline-success my-3 sticky-content " type="submit" href="/#/newProject">
            Neues Projekt <font-awesome-icon icon="fa-solid fa-plus" />
          </a>
        </div>
        <div class="flex-div">
          <div class="input-group searchProject">
            <span class="round-left input-group-text" id="basic-addon1">
              <font-awesome-icon icon="fa-solid fa-search" /></span>
            <div class="form-floating">
              <input type="text" id="floatingInputSearchProject" class="form-control" v-model="state.searchProject"
                placeholder="Projektsuche" />
              <label for="floatingInputSearchProject">Projektsuche</label>
            </div>
            <span :class="{ grey: !state.searchProject.length }" class="round-right input-group-text resetSearchProject"
              @click.prevent="state.searchProject = ''">
              <font-awesome-icon icon="fa-solid fa-xmark" />
            </span>
          </div>
        </div>
        <div class="flex-div"><!-- Don't remove (necessary for middle-positioning) --></div>
      </div>

      <h1 v-if="state.new_homework.length">Aktuelle Hausaufgaben</h1>
      <div class="d-flex align-content-start flex-wrap">
        <!-- if teacher: -->
        <ProjectCard v-if="authStore.isTeacher()" v-for="(h, index) in newHomeworkFiltered" :key="`${index}-${h.id}`"
          isHomework isTeacher :name="h.name" :description="h.description" :id="h.id" :deadline="h.deadline"
          :courseName="h.course_name" :courseColor="h.course_color" :courseFontDark="h.course_font_dark"
          @renameHomework="askRenameHomework" @deleteHomework="askDeleteHomework" @addSolution="addSolution" />

        <!-- else -->
        <ProjectCard v-else v-for="(h, index2) in newHomeworkFiltered" :key="`${index2}-${h.id}`" isHomework
          @startHomework="startHomework" :isEditing="h.is_editing" :name="h.name" :description="h.description"
          :uuid="h.uuid" :branch="h.branch" :id="h.id" :deadline="h.deadline"
          @deleteHomeworkBranch="askDeleteHomeworkBranch" />
      </div>

      <h1 v-if="state.old_homework.length">Frühere Hausaufgaben</h1>
      <div class="d-flex align-content-start flex-wrap">
        <!-- if teacher: -->
        <ProjectCard v-if="authStore.isTeacher()" v-for="(h, index) in oldHomeworkFiltered" :key="`${index}-${h.id}`"
          isHomework isOld isTeacher :name="h.name" :description="h.description" :id="h.id" :deadline="h.deadline"
          :courseName="h.course_name" :courseColor="h.course_color" :courseFontDark="h.course_font_dark"
          @renameHomework="askRenameHomework" @deleteHomework="askDeleteHomework" />

        <!-- else -->
        <ProjectCard v-else v-for="(h, index2) in oldHomeworkFiltered" :key="`${index2}-${h.id}`" isHomework isOld
          @startHomework="startHomework" :isEditing="h.is_editing" :name="h.name" :uuid="h.uuid"
          :description="h.description" :branch="h.branch" :id="h.id" :deadline="h.deadline"
          @deleteHomeworkBranch="askDeleteHomeworkBranch" />
      </div>

      <h1 v-if="state.myProjects.length">
        Meine Projekte
        <div v-if="state.isDuplicating" class="spinner-border text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </h1>
      <div class="d-flex align-content-start flex-wrap">
        <ProjectCard v-for="(p, index) in myProjectsFiltered" :name="p.name" :description="p.description" :uuid="p.uuid"
          :key="`${index}-${p.uuid}`" @renameProject="askRenameProject" @duplicateProject="duplicateProject"
          @downloadProject="downloadProject" @deleteProject="askDeleteProject" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.flex-div {
  flex: 1;
  display: flex;
  justify-content: center;
}

.flex-div:first-child>a {
  margin-right: auto;
}

/* .flex-div:last-child {
  margin-left: auto;
} */

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
