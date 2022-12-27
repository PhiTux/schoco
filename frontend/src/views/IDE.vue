<script setup>
import { onBeforeMount, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Toast } from "bootstrap";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import CodeService from "../services/code.service";
import IDEFileTree from "../components/IDEFileTree.vue";
import 'ace-builds';
import 'ace-builds/src-min-noconflict/mode-java'
import 'ace-builds/src-min-noconflict/theme-monokai'
import 'ace-builds/src-min-noconflict/ext-language_tools'


const route = useRoute();

let state = reactive({
  projectName: "",
  files: [],
  content: ["huhu"]
});



function editorInit() {
  var editor = ace.edit('editor')
  editor.setOptions({
    tabSize: 4,
    useSoftTabs: true,
    navigateWithinSoftTabs: true,
    fontSize: 16,
    scrollPastEnd: 0.5,
    enableBasicAutocompletion: true,
    showPrintMargin: false
  })
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
      console.log(error);
    }
  );
});

function openFile(path) {
  console.log(path)
}
</script>

<template>
  <div class="ide">
    <!-- Toasts -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastLoadingProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Laden des Projekts. Bitte zurück oder neu laden.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastProjectAccessError" role="alert"
        aria-live="assertive" aria-atomic="true">
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
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item dropdown mx-3">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"
                aria-expanded="false">
                Projekt
              </a>
              <ul class="dropdown-menu">
                <li>
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-file-circle-plus" />
                    Neue Datei</a>
                </li>
                <li>
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-folder-plus" /> Neuer
                    Ordner</a>
                </li>
                <li>
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-trash" /> Datei/Ordner
                    löschen</a>
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>
                <li>
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-floppy-disk" />
                    Änderungen speichern</a>
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>

                <li>
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-xmark" /> Projekt
                    schließen</a>
                </li>
              </ul>
            </li>
            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-left-long" />
              </button>
              <button type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-rotate-right" />
              </button>
            </div>

            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button type="button" class="btn btn-green">
                <font-awesome-icon icon="fa-solid fa-floppy-disk" /> Speichern
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
      <splitpanes class="default-theme" height="100%" horizontal :push-other-panes="false">
        <pane>
          <splitpanes :push-other-panes="false">
            <pane min-size="15" size="20" max-size="30" style="background-color: #383838">
              <div class="projectName"></div>
              <IDEFileTree :files="state.files" @openFile="openFile" />
            </pane>
            <pane>
              <v-ace-editor id="editor" v-model:value="state.content[0]" @init="editorInit" lang="java"
                theme="monokai" />
            </pane>
          </splitpanes>
        </pane>
        <pane max-size="50" size="20">
          <span>5</span>
        </pane>
      </splitpanes>
    </div>
  </div>
</template>

<style scoped>
#editor {
  width: 100%;
  height: 100%;
}

.projectName {
  background-color: red;
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
