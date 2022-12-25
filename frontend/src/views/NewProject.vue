<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { Toast } from "bootstrap";
import CodeService from "../services/code.service";

const router = useRouter();

let state = reactive({
  helloWorldName: "",
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

  router.push({
    name: "ide",
    params: { project_uuid: "0840baae-eca9-450b-885a-e0759d60f028" },
  });
  return;

  CodeService.createNewHelloWorld(state.helloWorldName).then(
    (response) => {
      console.log(response.data);
    },
    (error) => {
      console.log(error);
    }
  );
}
</script>

<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div
      class="toast align-items-center text-bg-danger border-0"
      id="toastProjectNameTooShort"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          Du musst einen Projektnamen mit mindestens 3 Zeichen eingeben.
        </div>
      </div>
    </div>
  </div>
  <div class="container">
    <h1>Wähle dein Ausgangs-Projekt</h1>
    <h2>1) Hello World</h2>

    <div class="row">
      <div class="col-md-4 col-sm-6">
        <div class="form-floating">
          <input
            type="text"
            id="floatingInputHelloWorld"
            class="form-control"
            v-model="state.helloWorldName"
            placeholder="Neuer Projektname"
          />
          <label class="input-label" for="floatingInputHelloWorld"
            >Neuer Projektname</label
          >
        </div>
      </div>
      <div class="col">
        <button
          class="btn btn-outline-success my-3"
          type="submit"
          @click.prevent="newHelloWorld()"
          :disabled="state.creatingProject"
        >
          <span
            class="spinner-border spinner-border-sm"
            role="status"
            aria-hidden="true"
            v-if="state.creatingProject"
          ></span>
          'Hello World'-Standard-Projekt
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
