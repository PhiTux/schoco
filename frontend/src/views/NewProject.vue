<script setup>
import { reactive, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { Toast, Popover } from "bootstrap";
import CodeService from "../services/code.service.js";
import FileUpload from 'vue-upload-component'
import { useI18n } from 'vue-i18n'

const i18n = useI18n()

const router = useRouter();

let state = reactive({
  helloWorldName: "",
  className: "",
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

  document.title = i18n.t("new_project_title")

  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new Popover(popoverTriggerEl))
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
    } else if (file.size > 20000000) {
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

  if (state.className.trim() === "") {
    const toast = new Toast(
      document.getElementById("toastClassNameEmpty")
    );
    toast.show();
    return;
  }

  if (/^[^a-zA-Z]/.test(state.className) || /[^a-zA-Z0-9_]/.test(state.className) || state.className.includes(" ")) {
    console.log(state.className)
    const toast = new Toast(
      document.getElementById("toastClassNameIllegal")
    );
    toast.show();
    return;
  }

  state.creatingProject = true;

  CodeService.createNewHelloWorld(state.helloWorldName.trim(), state.className.trim(), state.helloWorldDescription, i18n.locale.value).then(
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

    CodeService.uploadProject(file).then(
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
            {{ $t("project_name_must_not_be_empty") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastClassNameEmpty" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("class_name_must_not_be_empty") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastClassNameIllegal" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("class_name_illegal") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastProjectNotCreated" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("project_could_not_be_created") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastFileNotZip" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("only_zip_files_allowed") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastFileTooLarge" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("file_too_large") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUploadError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("project_import_failed") }}
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastUploadSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i18n-t keypath="project_import_success" tag="span">
              <router-link to="/home">{{ $t("home_title") }}</router-link>
            </i18n-t>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <h2 class="mt-4">{{ $t("new_empty_project") }}</h2>

      <div class="row">
        <div class="col-md-4 col-sm-6 d-flex flex-column justify-space-between">
          <div class="form-floating">
            <input type="text" id="HelloWorldName" class="form-control" v-model="state.helloWorldName"
              :placeholder="$t('project_name')" @keyup.enter="newHelloWorld()" />
            <label for="HelloWorldName">{{ $t("project_name") }}*</label>
          </div>
          <div class="d-flex flex-row align-items-center">
            <div class="form-floating mt-2 flex-fill">
              <input type="text" id="className" class="form-control" v-model="state.className"
                :placeholder="$t('class_name')" @keyup.enter="newHelloWorld()" />
              <label for="className">{{ $t("class_name") }}*</label>
            </div>
            <a class="btn btn-round" tabindex="0" data-bs-trigger="focus" data-bs-toggle="popover"
              :data-bs-content="$t('classname_explanation')">
              <font-awesome-icon icon="fa-solid fa-question-circle" size="lg" style="color: var(--bs-primary)" />
            </a>
          </div>

        </div>
        <div class="col-md-4 col-sm-6">
          <div class="form-floating">
            <textarea id="HelloWorldDescription" class="form-control" v-model="state.helloWorldDescription"
              :placeholder="$t('project_description')" rows="4" />
            <label for="HelloWorldDescription">{{ $t("project_description") }}</label>
          </div>
        </div>
        <div class="col">
          <button class="btn btn-outline-success my-3" type="submit" @click.prevent="newHelloWorld()"
            :disabled="state.creatingProject">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"
              v-if="state.creatingProject"></span>
            {{ $t("create_project") }}
          </button>
        </div>
      </div>

      <!-- <h2>2) Vorlage wählen</h2> -->
      <div class="or">{{ $t("or") }}</div>

      <h2>{{ $t("upload_zips") }}</h2>
      {{ $t("upload_zips_description") }}
      <div class="example-drag d-flex justify-content-center my-3">
        <file-upload class="d-flex justify-content-center align-items-center droparea" id="droparea"
          post-action="/upload/post" accept="application/zip" :multiple="true" :drop="true" extensions="zip"
          v-model="state.files" ref="upload">
          <font-awesome-icon icon="fa-solid fa-upload"></font-awesome-icon>
        </file-upload>
        <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
          <h3>{{ $t("drop_files_to_upload") }}</h3>
        </div>
      </div>

      <div v-if="state.files.length">
        <h5>{{ $t("selected_files") }}</h5>
        <ul>
          <li v-for="(  file, index  ) in   state.files  " :key="file.name" class="d-flex align-items-center">
            <font-awesome-icon v-if="state.successIndexes.includes(index)" icon="fa-circle-check" class="greenLabel" />
            <font-awesome-icon v-else-if="state.errorIndexes.includes(index)" icon="fa-triangle-exclamation"
              class="redLabel" />
            <div v-else-if="state.uploadIndexes.includes(index)" class="spinner-border spinner-border-sm text-warning"
              role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <font-awesome-icon v-else icon="fa-list-ul" />

            <span class="mx-2"><b :class="{ redLabel: state.errorIndexes.includes(index) }"><u>{{ file.name }}</u></b>
              ({{
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
          {{ $t("upload") }}
        </button>
        <button v-else class="btn btn-outline-success my-3" type="submit" @click.prevent="resetFileList()">
          {{ $t("reset_file_list") }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.justify-space-between {
  justify-content: space-between;
}

.or {
  font-size: 20px;
  font-style: italic;
  text-decoration: underline;
  text-decoration-color: red;
  margin-top: 1em;
  margin-bottom: 1em;
}

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

#HelloWorldDescription {
  height: 100%;
  font-family: monospace;
}
</style>
