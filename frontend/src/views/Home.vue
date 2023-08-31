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


      <div class="toast align-items-center text-bg-success border-0" id="toastAddSolutionSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Lösung wurde hinzugefügt.</div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastAddSolutionError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">Fehler beim Zufügen der Lösung.</div>
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

            <div v-if="authStore.isTeacher()" class="mt-3 alert alert-warning">
              Falls dieses Projekt als Lösung hinterlegt ist, dann wird auch diese Verknüpfung gelöscht.
            </div>
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

    <div class="modal fade" id="editSolutionModal" tabindex="-1" aria-labelledby="editSolutionModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">
              <span v-if="state.solution_id == null">Lösung hinzufügen</span>
              <span v-else>Lösung ändern</span>
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              Wähle ein privates Projekt aus, welches die Schüler ab einem bestimmten Zeitpunkt als Lösung anschauen
              können. Die Schüler können die Lösung nur öffnen und ausführen, aber nicht bearbeiten.
            </div>
            <label class="form-label">Wähle die Lösung:</label>
            <v-select :options="state.myProjects" v-model="state.solution_id" label="name" :reduce="p => p.id"
              placeholder="">
            </v-select>
            <br>
            <br>
            <label class="form-label">Ab wann soll die Lösung sichtbar sein?</label>
            <div class="d-flex flex-row align-items-center">
              <button type="button" class="btn btn-primary btn-sm"
                @click.prevent="state.solution_start_showing = new Date()">
                Ab sofort
              </button>
              <span class="mx-2"><b>oder</b></span>
              <VueDatePicker class="flex-fill" v-model="state.solution_start_showing" placeholder="Datum wählen ..."
                text-input auto-apply :min-date="new Date()" prevent-min-max-navigation locale="de"
                format="E dd.MM.yyyy, HH:mm" />
            </div>
            <font-awesome-icon icon="fa-solid fa-arrow-right" fixed-width />
            <span v-if="state.solution_start_showing === ''"><em class="text-bg-warning">Eingabe fehlt</em></span>
            <span v-else-if="(new Date(state.solution_start_showing) <= new Date())"><b>Sichtbar ab
                <u>sofort</u></b>
            </span>
            <span v-else><b>Sichtbar in <u>{{
              Math.floor((new Date(state.solution_start_showing)
                -
                new
                  Date()) / (1000 * 3600 * 24)) }} Tage,
                  {{ Math.floor((new Date(state.solution_start_showing) - new Date()) / (1000 * 3600) % 24) }}
                  Stunden</u></b>
            </span>
            <br>

            <div v-if="state.addSolutionInputInvalid" class="alert alert-danger mt-4">
              Lösung konnte nicht gespeichert werden. Überprüfe deine Eingaben.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button @click.prevent="addSolution()" type="button" class="btn btn-primary" :disabled="!state.solution_id">
              <div v-if="!state.isAddingSolution">Speichern</div>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container main">
      <div class="d-flex flex-row flex-wrap align-items-center justify-content-center">
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
          :solution_name="h.solution_name" :solution_start_showing="h.solution_start_showing" :solution_id="h.solution_id"
          @renameHomework="askRenameHomework" @deleteHomework="askDeleteHomework" @addSolution="openAddSolutionModal" />

        <!-- else -->
        <ProjectCard v-else v-for="(h, index2) in newHomeworkFiltered" :key="`${index2}-${h.id}`" isHomework
          @startHomework="startHomework" :isEditing="h.is_editing" :name="h.name" :description="h.description"
          :uuid="h.uuid" :branch="h.branch" :id="h.id" :deadline="h.deadline" :solution_uuid="h.solution_uuid"
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
