<script setup>
import { onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import { Toast } from "bootstrap";
import CodeService from "../services/code.service";

const route = useRoute();

onBeforeMount(() => {
  CodeService.loadAllFiles(route.params.project_uuid).then(
    (response) => {
      console.log(response.data);
      // TODO: https://stackoverflow.com/questions/36248245/how-to-convert-an-array-of-paths-into-json-structure
      // -> die response-liste mit files in json umwandeln
    },
    (error) => {
      if (error.response.status == 405) {
        const toast = new Toast(
          document.getElementById("toastProjectAccessError")
        );
        toast.show();
      } else {
        console.log(error.response);

        if (error.response.status == 500) {
          const toast = new Toast(
            document.getElementById("toastLoadingProjectError")
          );
          toast.show();
        }
      }
    }
  );
});
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
    <nav class="navbar sticky-top bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Sticky top</a>
      </div>
    </nav>

    <h1>IDE</h1>
  </div>
</template>

<style scoped>
.main {
  padding-top: 0px !important;
}
</style>
