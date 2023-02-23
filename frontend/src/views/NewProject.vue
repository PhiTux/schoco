<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { Toast } from "bootstrap";
import CodeService from "../services/code.service.js";

const router = useRouter();

let state = reactive({
  helloWorldName: "",
  helloWorldDescription: "",
  creatingProject: false,
});

function newHelloWorld() {
  if (state.helloWorldName.length < 3) {
    const toast = new Toast(
      document.getElementById("toastProjectNameTooShort")
    );
    toast.show();
    return;
  }

  state.creatingProject = true;

  /* router.push({
    name: "ide",
    params: { project_uuid: "0840baae-eca9-450b-885a-e0759d60f028" },
  });
  return; */

  CodeService.createNewHelloWorld(state.helloWorldName, state.helloWorldDescription).then(
    (response) => {
      router.push({
        name: "ide",
        params: { project_uuid: response.data },
      });
    },
    (error) => {
      console.log(error.response);
      const toast = new Toast(
        document.getElementById("toastProjectNotCreated")
      );
      toast.show();
    }
  );
}
</script>

<template>
  <!-- Toasts -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div class="toast align-items-center text-bg-danger border-0" id="toastProjectNameTooShort" role="alert"
      aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Du musst einen Projektnamen mit mindestens 3 Zeichen eingeben.
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

    <h2>2) Vorlage wählen</h2>
    <h2>3) Zip hochladen</h2>
  </div>
</template>

<style scoped>
.input-label {
  color: var(--bs-dark);
}
</style>
