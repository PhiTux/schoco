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
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-floppy-disk" />
                    Änderungen speichern</a
                  >
                </li>
                <li><hr class="dropdown-divider" /></li>

                <li>
                  <a class="dropdown-item" href="#"
                    ><font-awesome-icon icon="fa-solid fa-xmark" /> Projekt
                    schließen</a
                  >
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

    <h1>IDE</h1>
  </div>
</template>

<style scoped>
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
