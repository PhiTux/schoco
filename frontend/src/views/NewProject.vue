<script setup>
import { reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { Toast } from "bootstrap";
import CodeService from "../services/code.service.js";
/* import DropArea from "../components/DropArea.vue"; */
import FileUpload from 'vue-upload-component'

const router = useRouter();

let state = reactive({
  helloWorldName: "",
  helloWorldDescription: "",
  creatingProject: false,
  files: [],
  uploadIndexes: [],
  successIndexes: [],
  errorIndexes: [],
  uploadFinished: false,
});

onMounted(() => {
  // set cursor to pointer for upload-label
  let elem = document.getElementById("droparea");
  let children = elem.childNodes;
  // get element which is label
  children.forEach((e) => {
    if (e.nodeName == "LABEL") {
      e.style = "cursor: pointer;"
    }
  })
})

watch(() => state.files, (files) => {
  for (let i = files.length - 1; i >= 0; i--) {
    let file = files[i];
    if (!file.name.endsWith(".zip")) {
      const toast = new Toast(
        document.getElementById("toastFileNotZip")
      );
      toast.show();
      state.files.splice(i, 1);
    } else if (file.size > 5000000) {
      const toast = new Toast(
        document.getElementById("toastFileTooLarge")
      );
      toast.show();
      state.files.splice(i, 1);
    }
  }
})

function newHelloWorld() {
  if (state.helloWorldName.trim() === "") {
    const toast = new Toast(
      document.getElementById("toastProjectNameEmpty")
    );
    toast.show();
    return;
  }

  state.creatingProject = true;

  CodeService.createNewHelloWorld(state.helloWorldName.trim(), state.helloWorldDescription).then(
    (response) => {
      state.creatingProject = false;
      router.push({
        name: "ide",
        params: { project_uuid: response.data, user_id: 0 },
      });
    },
    (error) => {
      console.log(error.response);
      state.creatingProject = false;

      if (error.response.status === 400) {
        const toast = new Toast(
          document.getElementById("toastProjectNameEmpty")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastProjectNotCreated")
        );
        toast.show();
      }


    }
  );
}

function removeFile(index) {
  state.files.splice(index, 1);
}

function uploadFiles() {

  state.uploadIndexes = [];
  state.successIndexes = [];
  state.errorIndexes = [];

  for (let i = 0; i < state.files.length; i++) {
    let file = state.files[i]
    state.uploadIndexes.push(i);

    CodeService.uploadProject(file, {
      // TODO: check if this is needed
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        console.log(percentCompleted);
      }
    }).then(
      (response) => {

        const index = state.uploadIndexes.indexOf(i);
        if (index > -1) {
          state.uploadIndexes.splice(index, 1);
        }

        if (response.data) {
          state.successIndexes.push(i);
        } else {
          state.errorIndexes.push(i);
        }

        checkUploadFinished();
      },
      (error) => {
        const index = state.uploadIndexes.indexOf(i);
        if (index > -1) {
          state.uploadIndexes.splice(index, 1);
        }
        state.errorIndexes.push(i);

        checkUploadFinished();
        console.log(error.response);
      }
    );
  }
}

function checkUploadFinished() {
  if (state.uploadIndexes.length === 0) {
    state.uploadFinished = true;

    if (state.errorIndexes.length > 0) {
      const toast = new Toast(
        document.getElementById("toastUploadError")
      );
      toast.show();
    } else {
      const toast = new Toast(
        document.getElementById("toastUploadSuccess")
      );
      toast.show();
    }

  }
}

function resetFileList() {
  state.files = [];
  state.uploadIndexes = [];
  state.successIndexes = [];
  state.errorIndexes = [];
  state.uploadFinished = false;
}
</script>

<template>
  <div>
    <!-- Toasts -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastProjectNameEmpty" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Dein Projektname darf nicht leer sein.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastProjectNotCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Das Projekt konnte leider nicht erstellt werden.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastFileNotZip" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Nur Zip-Dateien erlaubt.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastFileTooLarge" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Eine ausgewählte Datei ist zu groß (> 5 MB).
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUploadError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Nicht alle Projekte konnten importiert werden!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastUploadSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Alle Projekte wurden importiert!
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <h1>Wähle dein Ausgangs-Projekt</h1>
      <h2>1) Neues "leeres" Projekt</h2>

      <div class="row">
        <div class="col-md-4 col-sm-6">
          <label for="HelloWorldName">Neuer Projektname</label>
          <input type="text" id="HelloWorldName" class="form-control" v-model="state.helloWorldName"
            placeholder="Neuer Projektname" />
        </div>
        <div class="col-md-4 col-sm-6">
          <label for="HelloWorldDescription">Projektbeschreibung</label>
          <textarea id="HelloWorldDescription" class="form-control" v-model="state.helloWorldDescription"
            placeholder="Projektbeschreibung" rows="3" />
        </div>
        <div class="col">
          <button class="btn btn-outline-success my-3" type="submit" @click.prevent="newHelloWorld()"
            :disabled="state.creatingProject">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
              v-if="state.creatingProject"></span>
            Projekt erstellen
          </button>
        </div>
      </div>

      <!-- <h2>2) Vorlage wählen</h2> -->

      <h2>2) Zip hochladen</h2>
      Lade zuvor exportierte Projekte hoch. Es können mehrere Projekte auf einmal hochgeladen werden.
      <div class="example-drag d-flex justify-content-center my-3">
        <!-- <div class=""> -->
        <file-upload class="d-flex justify-content-center align-items-center droparea" id="droparea"
          post-action="/upload/post" accept="application/zip" :multiple="true" :drop="true" extensions="zip"
          v-model="state.files" ref="upload">
          <!-- <i class="fa fa-plus"></i> -->
          <font-awesome-icon icon="fa-solid fa-upload"></font-awesome-icon>
        </file-upload>
        <!-- </div> -->
        <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
          <h3>Dateien zum Hochladen ablegen</h3>
        </div>
      </div>

      <div v-if="state.files.length">
        <h5>Ausgewählte Dateien:</h5>
        <ul>
          <li v-for="(file, index) in state.files" :key="file.name" class="d-flex align-items-center">
            <font-awesome-icon v-if="state.successIndexes.includes(index)" icon="fa-circle-check" class="greenLabel" />
            <font-awesome-icon v-else-if="state.errorIndexes.includes(index)" icon="fa-triangle-exclamation"
              class="redLabel" />
            <div v-else-if="state.uploadIndexes.includes(index)" class="spinner-border spinner-border-sm text-warning"
              role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <font-awesome-icon v-else icon="fa-list-ul" />

            <span class="mx-2"><b :class="{ redLabel: state.errorIndexes.includes(index) }"><u>{{ file.name }}</u></b> ({{
              file.size / 1000 }} kB)</span>

            <a v-if="state.uploadIndexes.length + state.successIndexes.length + state.errorIndexes.length == 0"
              class="btn-remove d-flex align-items-center" @click="removeFile(index)">
              <font-awesome-layers class="fa-lg">
                <font-awesome-icon icon="fa-circle" style="color: var(--bs-danger)" />
                <div style="color: var(--bs-light)">
                  <font-awesome-icon icon="fa-xmark" transform="shrink-6" />
                </div>
              </font-awesome-layers>
            </a>
          </li>
        </ul>
        <button v-if="!state.uploadFinished" class="btn btn-outline-success my-3" type="submit"
          @click.prevent="uploadFiles()">
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
            v-if="state.uploadIndexes.length"></span>
          Hochladen
        </button>
        <button v-else class="btn btn-outline-success my-3" type="submit" @click.prevent="resetFileList()">
          Datei-Liste zurücksetzen
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.greenLabel {
  color: var(--bs-success);
}

.redLabel {
  color: var(--bs-danger);
}

.btn-remove {
  cursor: pointer;
}

.example-drag label.btn {
  margin-bottom: 0;
  margin-right: 1rem;
}

.droparea:hover .fa-upload {
  scale: 4.5;
}

.fa-upload {
  scale: 4;
  box-shadow: 0 0 10px black;
  padding: 7px;
  border-radius: 5px;
  transition: all 0.3s ease-in-out;
}


.example-drag .drop-active {
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  position: fixed;
  z-index: 9999;
  opacity: .6;
  text-align: center;
  background: #000;
}

.example-drag .drop-active h3 {
  margin: -.5em 0 0;
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  -webkit-transform: translateY(-50%);
  -ms-transform: translateY(-50%);
  transform: translateY(-50%);
  font-size: 40px;
  color: #fff;
  padding: 0;
}

.droparea {
  border: 4px dashed #000;
  border-radius: 25px;
  width: 90%;
  height: 200px;
  color: grey;
}
</style>
