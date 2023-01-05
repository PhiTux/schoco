<script setup>
import { onBeforeMount, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Toast } from "bootstrap";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import CodeService from "../services/code.service";
import IDEFileTree from "../components/IDEFileTree.vue";
import "ace-builds";
import "ace-builds/src-min-noconflict/mode-java";
import "ace-builds/src-min-noconflict/theme-monokai";
import "ace-builds/src-min-noconflict/ext-language_tools";

const route = useRoute();

let state = reactive({
  projectName: "",
  files: [],
  openFiles: [],
  activeTab: 0,
  tabsWithChanges: [],
  isSaving: false,
});

function editorChange() {
  for (let i = 0; i < state.openFiles.length; i++) {
    if (state.openFiles[i]["tab"] == state.activeTab) {
      var editor = ace.edit("editor");
      // if no change to original
      if (state.openFiles[i]["content"] == editor.getSession().getValue()) {
        if (state.tabsWithChanges.includes(state.activeTab)) {
          for (let x = 0; x < state.tabsWithChanges.length; x++) {
            if (state.tabsWithChanges[x] === state.activeTab) {
              state.tabsWithChanges.splice(x, 1);
              break;
            }
          }
        }
      } else {
        if (!state.tabsWithChanges.includes(state.activeTab)) {
          state.tabsWithChanges.push(state.activeTab);
        }
      }

      break;
    }
  }
}

function editorInit() {
  var editor = ace.edit("editor");
  editor.setOptions({
    tabSize: 4,
    useSoftTabs: true,
    navigateWithinSoftTabs: true,
    fontSize: 16,
    scrollPastEnd: 0.5,
    enableBasicAutocompletion: true,
    showPrintMargin: false,
  });
  editor.on("change", editorChange);
}

onBeforeMount(() => {
  CodeService.loadAllFiles(route.params.project_uuid).then(
    (response) => {
      if (response.status == 200) {
        state.files = response.data;
      }
    },
    (error) => {
      if (
        typeof error.response === "undefined" ||
        error.response.status == 500
      ) {
        const toast = new Toast(
          document.getElementById("toastLoadingProjectError")
        );
        toast.show();
      } else {
        console.log(error.response);

        if (error.response.status == 405) {
          const toast = new Toast(
            document.getElementById("toastProjectAccessError")
          );
          toast.show();
        }
      }
    }
  );

  CodeService.getProjectName(route.params.project_uuid).then(
    (response) => {
      if (response.status == 200) state.projectName = response.data;
    },
    (error) => {
      //console.log(error);
    }
  );
});

function openFile(inputPath) {
  let path = inputPath;
  if (inputPath.endsWith("/")) {
    path = inputPath.slice(0, -1);
  }

  // check if Tab is already existing
  let tab = -1;
  for (let i = 0; i < state.openFiles.length; i++) {
    if (state.openFiles[i].path === path) {
      tab = state.openFiles[i].tab;
      break;
    }
  }

  // it's not yet open
  if (tab == -1) {
    let content = "";
    for (let i = 0; i < state.files.length; i++) {
      if (state.files[i]["path"] === path) {
        content = state.files[i]["content"];
        break;
      }
    }
    let newTab = 0;
    for (let i = 0; i < state.openFiles.length; i++) {
      if (state.openFiles[i].tab > newTab) {
        newTab = state.openFiles[i].tab;
      }
    }

    tab = newTab + 1;

    let session = ace.createEditSession(content, "ace/mode/java");

    let newFileTab = {
      path: path,
      content: content,
      tab: tab,
      session: session,
    };
    let editor = ace.edit("editor");
    editor.setSession(session);
    editor.focus();

    state.openFiles.push(newFileTab);
    state.activeTab = tab;
    return;
  }

  // find session in openFiles
  for (let i = 0; i < state.openFiles.length; i++) {
    if (state.openFiles[i].tab == tab) {
      let editor = ace.edit("editor");
      editor.setSession(state.openFiles[i]["session"]);
      editor.focus();
      state.activeTab = tab;
      break;
    }
  }
}

function undo() {
  ace.edit("editor").session.getUndoManager().undo();
  ace.edit("editor").focus();
}

function redo() {
  ace.edit("editor").session.getUndoManager().redo();
  ace.edit("editor").focus();
}

function updateTabsWithChanges() {
  while (state.tabsWithChanges.length) {
    state.tabsWithChanges.pop();
  }
  for (let i = 0; i < state.openFiles.length; i++) {
    if (
      state.openFiles[i]["session"].getValue() != state.openFiles[i]["content"]
    ) {
      state.tabsWithChanges.push(state.openFiles[i]["tab"]);
    }
  }
}

function saveAll() {
  state.isSaving = true;

  let changes = [];
  for (let i = 0; i < state.tabsWithChanges.length; i++) {
    for (let x = 0; x < state.openFiles.length; x++) {
      if (state.openFiles[x]["tab"] === state.tabsWithChanges[i]) {
        let sha = "";
        for (let y = 0; y < state.files.length; y++) {
          if (state.files[y]["path"] === state.openFiles[x]["path"]) {
            sha = state.files[y]["sha"];
            break;
          }
        }
        changes.push({
          path: state.openFiles[x]["path"],
          content: state.openFiles[x]["session"].getValue(),
          sha: sha,
        });
        continue;
      }
    }
  }

  CodeService.saveFileChanges(changes, route.params.project_uuid).then(
    (response) => {
      state.isSaving = false;

      for (let i = 0; i < response.data.length; i++) {
        for (let x = 0; x < state.files.length; x++) {
          if (state.files[x]["path"] === response.data[i]["path"]) {
            state.files[x]["sha"] = response.data[i]["sha"];
            state.files[x]["content"] = response.data[i]["content"];
            continue;
          }
        }
        for (let x = 0; x < state.openFiles.length; x++) {
          if (state.openFiles[x]["path"] === response.data[i]["path"]) {
            state.openFiles[x]["content"] = response.data[i]["content"];
          }
        }
      }

      //editorChange()
      updateTabsWithChanges();
      ace.edit("editor").focus();
    },
    (error) => {
      state.isSaving = false;
      console.log(error);
    }
  );
}
</script>

<template>
  <div class="ide">
    <!-- Toasts -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div
        class="toast align-items-center text-bg-danger border-0"
        id="toastLoadingProjectError"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Laden des Projekts. Bitte zurück oder neu laden.
          </div>
        </div>
      </div>

      <div
        class="toast align-items-center text-bg-danger border-0"
        id="toastProjectAccessError"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            Du kannst nur deine eigenen Projekte öffnen!
          </div>
        </div>
      </div>
    </div>

    <!-- Navbar -->
    <nav class="navbar sticky-top navbar-expand-lg bg-dark navbar-dark">
      <div class="container-fluid">
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item dropdown mx-3">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                Projekt
              </a>
              <ul class="dropdown-menu">
                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-file-circle-plus" />
                    Neue Datei</a
                  >
                </li>
                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-folder-plus" /> Neuer
                    Ordner</a
                  >
                </li>
                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-trash" /> Datei/Ordner
                    löschen</a
                  >
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>

                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-xmark" /> Projekt
                    schließen</a
                  >
                </li>
              </ul>
            </li>
            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button
                @click.prevent="undo()"
                type="button"
                class="btn btn-outline-secondary"
              >
                <font-awesome-icon icon="fa-solid fa-arrow-left-long" />
              </button>
              <button
                @click.prevent="redo()"
                type="button"
                class="btn btn-outline-secondary"
              >
                <font-awesome-icon icon="fa-solid fa-arrow-rotate-right" />
              </button>
            </div>

            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button
                @click.prevent="saveAll()"
                type="button"
                class="btn btn-green"
                :disabled="state.tabsWithChanges.length == 0"
              >
                <div
                  v-if="state.isSaving"
                  class="spinner-border spinner-border-sm"
                  role="status"
                >
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-floppy-disk" />
                Speichern
              </button>
              <button type="button" class="btn btn-yellow">
                <font-awesome-icon icon="fa-solid btn-yellow fa-gear" />
                Kompilieren
              </button>
              <button type="button" class="btn btn-blue">
                <font-awesome-icon icon="fa-solid fa-circle-play" /> Ausführen
              </button>
              <button type="button" class="btn btn-indigo">
                <font-awesome-icon icon="fa-solid fa-list-check" /> Testen
              </button>
            </div>
          </ul>
        </div>
      </div>
    </nav>

    <div class="ide-main">
      <splitpanes
        class="default-theme"
        height="100%"
        horizontal
        :push-other-panes="false"
      >
        <pane>
          <splitpanes :push-other-panes="false">
            <pane
              min-size="15"
              size="20"
              max-size="30"
              style="background-color: #383838"
            >
              <div class="projectName">
                <p class="placeholder-wave" v-if="state.projectName === ''">
                  <span class="placeholder col-12"></span>
                </p>
                <p v-else class="d-flex justify-content-center m-auto">
                  {{ state.projectName }}
                </p>
              </div>
              <IDEFileTree :files="state.files" @openFile="openFile" />
            </pane>
            <pane>
              <ul class="nav nav-tabs pt-2">
                <li class="nav-item" v-for="f in state.openFiles">
                  <div
                    class="nav-link tab"
                    @click.prevent="openFile(f.path)"
                    :id="'fileTab' + f.tab"
                    :class="{
                      active: f.tab == state.activeTab,
                      changed: state.tabsWithChanges.includes(f.tab),
                    }"
                  >
                    {{ f.path }}
                  </div>
                </li>
              </ul>
              <v-ace-editor
                id="editor"
                v-model:value="state.projectName"
                @init="editorInit"
                lang="java"
                theme="monokai"
              />
            </pane>
          </splitpanes>
        </pane>
        <pane size="20" max-size="50">
          <span>5</span>
        </pane>
      </splitpanes>
    </div>
  </div>
</template>

<style scoped>
.changed {
  font-style: italic;
}

.changed::after {
  content: "*";
}

ul.nav-tabs {
  background-color: #383838;
}

.tab:not(.active) {
  border-left: 1px solid #ccc;
  border-top: 1px solid #ccc;
  border-right: 1px solid #ccc;
  background-color: #ddd;
}

.tab:hover {
  cursor: pointer;
}

.active {
  font-weight: bold;
}

#editor {
  width: 100%;
  height: 100%;
}

.projectName {
  /* background-color: red; */
  height: 56px;
}

.ide {
  height: 100vh;
}

.ide-main {
  height: calc(100% - 56px);
}

.btn-green {
  background-color: var(--green);
  color: var(--bs-light);
}

.btn-green:hover {
  background-color: var(--green-hover);
  color: var(--bs-light);
}

.btn-green:disabled {
  background-color: var(--green-disabled);
  color: var(--bs-light);
}

.btn-yellow {
  background-color: var(--yellow);
  color: var(--bs-dark);
}

.btn-yellow:hover {
  background-color: var(--yellow-hover);
  color: var(--bs-dark);
}

.btn-yellow:disabled {
  background-color: var(--yellow-disabled);
  color: var(--bs-light);
}

.btn-blue {
  background-color: var(--blue);
  color: var(--bs-light);
}

.btn-blue:hover {
  background-color: var(--blue-hover);
  color: var(--bs-light);
}

.btn-blue:disabled {
  background-color: var(--blue-disabled);
  color: var(--bs-light);
}

.btn-indigo {
  background-color: var(--indigo);
  color: var(--bs-light);
}

.btn-indigo:hover {
  background-color: var(--indigo-hover);
  color: var(--bs-light);
}

.btn-indigo:disabled {
  background-color: var(--indigo-disabled);
  color: var(--bs-light);
}
</style>
