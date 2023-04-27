<script setup>
import { onBeforeMount, reactive, watch, ref } from "vue";
import { useRoute } from "vue-router";
import { Toast, Popover, Modal } from "bootstrap";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import { useAuthStore } from "../stores/auth.store.js";
import CodeService from "../services/code.service.js";
import UserService from "../services/user.service.js"
import IDEFileTree from "../components/IDEFileTree.vue";
import CourseBadge from "../components/CourseBadge.vue"
import "ace-builds";
import "ace-builds/src-min-noconflict/mode-java";
import "ace-builds/src-min-noconflict/theme-monokai";
import "ace-builds/src-min-noconflict/ext-language_tools";
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'

const authStore = useAuthStore();
const route = useRoute();

let state = reactive({
  projectName: "",
  newProjectName: "",
  editingProjectName: false,
  isSavingProjectName: false,
  projectDescription: "",
  newProjectDescription: "",
  isSavingDescription: false,
  editingDescription: false,
  files: [],
  openFiles: [],
  activeTab: 0,
  tabsWithChanges: [],
  isSaving: false,
  isCompiling: false,
  isExecuting: false,
  isTesting: false,
  results: "",
  receivedWS: false,
  sendMessage: "",
  isHomework: false,
  fullUserName: "",
  deadline: "",
  websocket_open: false,
});

let homework = reactive({
  deadlineDate: new Date(),
  selectedCourse: "",
  computationTime: ""
})

let allCourses = ref([])

/** Stores the output displayed in the bottom pane. */
let results = ref("");

let ws;

window.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault()
    saveAll()
  }
})

watch(results, () => {
  let output = document.getElementById("output");
  output.scrollTop = output.scrollHeight;
});


function editorChange() {
  for (let i = 0; i < state.openFiles.length; i++) {
    if (state.openFiles[i]["tab"] == state.activeTab) {
      var editor = ace.edit("editor");
      // if no change to original
      if (state.openFiles[i]["content"] == editor.getSession().getValue()) {
        for (let x = 0; x < state.tabsWithChanges.length; x++) {
          if (state.tabsWithChanges[x] === state.activeTab) {
            state.tabsWithChanges.splice(x, 1);
            break;
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
  CodeService.loadAllFiles(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.status == 200) {
        state.files = response.data;
      }
      openFile("Schoco.java");
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

  CodeService.getProjectInfo(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.status == 200) {
        state.isHomework = response.data.isHomework;
        state.projectName = response.data.name;
        state.projectDescription = response.data.description;
        if (state.isHomework) {
          state.fullUserName = response.data.fullusername;
          state.deadline = response.data.deadline

          // show warning about editing the template
          if (route.params.user_id == 0) {
            var modal = new Modal(document.getElementById('templateWarningModal'));
            modal.show();
          }
        }
      }
    },
    (error) => {
      console.log(error);
    }
  );


  if (authStore.isTeacher()) {
    UserService.getAllCourses().then(
      (response) => {
        allCourses.value = response.data;
      },
      (error) => {
        if (error.response.status == 403) {
          const user = useAuthStore();
          user.logout();
        } else console.log(error.response);
      }
    );
  }
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
  if (state.isSaving || state.tabsWithChanges.length == 0) return;
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

  CodeService.saveFileChanges(changes, route.params.project_uuid, route.params.user_id).then(
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

function compile() {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  state.isCompiling = true;
  state.receivedWS = false;
  results.value = "";

  let projectFiles = [];
  for (let i = 0; i < state.files.length; i++) {
    projectFiles.push({
      path: state.files[i]["path"],
      content: state.files[i]["content"],
    });
  }

  CodeService.prepareCompile(projectFiles, route.params.project_uuid, route.params.user_id).then(
    (response) => {

      if (response.data.success == false) {
        state.isCompiling = false;
        results.value =
          "Der Server war leider gerade überlastet 😥 Bitte erneut versuchen!";
        return;
      }

      // attach WS(S)
      connectWebsocket(response.data.id);

      startCompile(
        response.data.ip,
        response.data.port,
        response.data.uuid,
        route.params.project_uuid,
        route.params.user_id
      );
    },
    (error) => {
      state.isCompiling = false;
      console.log(error.response);
    }
  );
}

function startCompile(ip, port, container_uuid, project_uuid, user_id) {
  CodeService.startCompile(ip, port, container_uuid, project_uuid, user_id).then(
    (response) => {
      state.isCompiling = false;
      if (response.data.status === "connect_error") {
        results.value =
          'Interner Verbindungsfehler ⚡ Vermutlich war der "Worker" (Teil des Servers, der u. a. kompiliert) einfach noch nicht soweit... \nBitte direkt erneut probieren 😊';
      } else if (!state.websocket_open) {
        showWSError();
      } else if (response.data.exitCode == 0 && !state.receivedWS) {
        results.value = "Erfolgreich kompiliert 🎉";
      }
    },
    (error) => {
      state.isCompiling = false;
      console.log(error.response);
    }
  );
}


function showWSError() {
  results.value = "Verbindungsfehler ⚡\nAktuell kann keine Ausgabe angezeigt werden.\n\nWenn das Problem bestehen bleibt, dann gib bitte deiner Lehrkraft Bescheid!";
}


function connectWebsocket(id) {
  // assume that URL==localhost means, that websocket-nginx works on port 80
  if (window.location.hostname === 'localhost' || window.location.hostname === "127.0.0.1") {
    var host = window.location.hostname + ':80'
  } else {
    var host = window.location.host
  }
  let protocol = window.location.protocol === "http:" ? "ws:" : "wss:"

  ws = new WebSocket(
    `${protocol}//${host}/containers/${id}/attach/ws?stream=1&stdin=1&stdout=1&stderr=1`
  );
  ws.binaryType = 'arraybuffer';

  ws.onmessage = function (event) {
    let dec = new TextDecoder();
    let msg = dec.decode(event.data);

    if (state.receivedWS == false) {
      state.receivedWS = true;
      results.value = "";
    }

    if (msg !== "\r\n" && msg.trim() === state.sendMessage.trim()) {
      state.sendMessage = ""
      return
    }

    results.value += msg;
  };

  ws.onerror = function (event) {
    state.websocket_open = false;
    showWSError();
    if (state.isCompiling) {
      state.isCompiling = false;
    } else if (state.isExecuting) {
      state.isExecuting = false;
    } else if (state.isTesting) {
      state.isTesting = false;
    }
  };

  ws.onopen = function (event) {
    state.websocket_open = true;
    if (state.isCompiling) {
      results.value = "Kompilierung gestartet... 🛠";
    } else if (state.isExecuting) {
      results.value = "Programm wird ausgeführt...";
    }
    //not used at the moment, since testing doesn't require WS...
    else if (state.isTesting) {
      results.value = "Programm wird getestet 📝➡️✅ bitte warten..."
    }
  };

  ws.onclose = function (event) {
    state.websocket_open = false;
    state.sendMessage = "";
  };
}

function execute() {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  state.isExecuting = true;
  state.receivedWS = false;

  results.value = "";

  CodeService.prepareExecute(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.data.executable == false) {
        results.value =
          "🔎 Leider keine ausführbaren Dateien gefunden. Bitte zuerst kompilieren ⚙";
        state.isExecuting = false;
        return;
      }

      connectWebsocket(response.data.id);

      startExecute(
        response.data.ip,
        response.data.port,
        response.data.uuid,
        route.params.project_uuid,
        route.params.user_id
      );
    },
    (error) => {
      state.isExecuting = false;
      console.log(error.response);
    }
  );
}

function startExecute(ip, port, uuid, project_uuid, user_id) {
  CodeService.startExecute(ip, port, uuid, project_uuid, user_id).then(
    (response) => {
      console.log("stopped executing")
      state.isExecuting = false;
    },
    (error) => {
      state.isExecuting = false;
      console.log(error.response);
    }
  );
}

function test() {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  state.isTesting = true;
  state.receivedWS = false;

  // using this line here (instead at opening WS), since Testing does not start a WS-connection
  results.value = "Programm wird getestet 📝➡️✅ bitte warten..."

  CodeService.prepareTest(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.data.executable == false) {
        results.value =
          "🔎 Leider keine ausführbaren Dateien gefunden. Bitte zuerst kompilieren ⚙";
        state.isTesting = false;
        return;
      }

      startTest(
        response.data.ip,
        response.data.port,
        response.data.uuid,
        route.params.project_uuid,
        route.params.user_id,
      );
    },
    (error) => {
      state.isTesting = false;
      console.log(error.response);
    }
  );
}


function startTest(ip, port, uuid, project_uuid, user_id) {
  CodeService.startTest(ip, port, uuid, project_uuid, user_id).then(
    (response) => {
      state.isTesting = false;

      results.value = ""

      if (response.data.status === "security_error") {
        results.value = "💥🙈 es gab wohl einen Sicherheitsfehler beim Testen deines Programms. Scheinbar hat dein Programm versucht, Dinge auszuführen, die nicht erlaubt sind. Korrigiere dies zuerst.\nWenn das Problem bestehen bleibt, solltest du dich an deine Lehrerin / deinen Lehrer wenden."
        return
      }

      if (response.data.failed_tests == 0) {
        results.value += "Alle Tests bestanden 🎉🤩\n\nDu kannst nun höchstens noch versuchen, deinen Quellcode zu \"verschönern\" ;-)"
      } else if (response.data.passed_tests == 0) {
        results.value += "Ups 🧐 Scheinbar wurde kein einziger Test bestanden! Vielleicht hilft dir die untere Ausgabe, um den Fehlern auf die Schliche zu kommen 🤗"
      }
      else {
        let percent = (response.data.passed_tests / (response.data.passed_tests + response.data.failed_tests)) * 100
        results.value += `Du hast ${percent}% der Tests bestanden. Vielleicht hilft dir die untere Ausgabe, um die restlichen Tests auch noch zu bestehen 🤗`
      }

      results.value += "\n\n==================\n\n"

      results.value += response.data.stdout
    },
    (error) => {
      results.value = "💥🙈 es gab wohl einen Fehler beim Testen deines Programms. Probiere es erneut!\nStelle zunächst sicher, dass dein Programm ausgeführt werden kann.\nWenn das Problem bestehen bleibt, solltest du dich an deine Lehrerin / deinen Lehrer wenden."
      state.isTesting = false;
      console.log(error.response);
    }
  );
}


function sendMessage() {
  ws.send(state.sendMessage + "\r");  // sending not possible without trailing \r...
}

function editProjectName() {
  state.newProjectName = state.projectName
  state.editingProjectName = true
}

function abortProjectName() {
  state.editingProjectName = false;
}

function saveProjectName() {
  if (state.isSavingProjectName) return;
  state.isSavingProjectName = true

  if (state.newProjectName.length < 3) {
    const toast = new Toast(
      document.getElementById("toastUpdateProjectNameTooShort")
    );
    toast.show();
    state.isSavingProjectName = false;
    return;
  }

  CodeService.updateProjectName(route.params.project_uuid, route.params.user_id, state.newProjectName).then(
    (response) => {
      if (response.data) {
        state.projectName = state.newProjectName;
        state.isSavingProjectName = false;
        state.editingProjectName = false;
      } else {
        const toast = new Toast(
          document.getElementById("toastUpdateProjectNameError")
        );
        toast.show();
        state.isSavingProjectName = false;
        state.editingProjectName = false;
      }
    },
    (error) => {
      if (error.response.status === 400) {
        const toast = new Toast(
          document.getElementById("toastUpdateProjectNameTooShort")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastUpdateProjectNameError")
        );
        toast.show();
      }


      state.isSavingProjectName = false;
      state.editingProjectName = false;
    }
  );
}

function editDescription() {
  state.newProjectDescription = state.projectDescription
  state.editingDescription = true
}

function abortDescription() {
  state.editingDescription = false;
}

function saveDescription() {
  if (state.isSavingDescription) return;
  state.isSavingDescription = true

  CodeService.updateDescription(route.params.project_uuid, route.params.user_id, state.newProjectDescription).then(
    (response) => {
      if (response.data) {
        state.projectDescription = state.newProjectDescription;
        state.isSavingDescription = false;
        state.editingDescription = false;
      } else {
        const toast = new Toast(
          document.getElementById("toastUpdateDescriptionError")
        );
        toast.show();
        state.isSavingDescription = false;
        state.editingDescription = false;
      }
    },
    (error) => {
      const toast = new Toast(
        document.getElementById("toastUpdateDescriptionError")
      );
      toast.show();
      state.isSavingDescription = false;
      state.editingDescription = false;
      console.log(error.response)
    }
  );
}

function createHomework() {
  let projectFiles = [];
  for (let i = 0; i < state.files.length; i++) {
    projectFiles.push({
      path: state.files[i]["path"],
      content: state.files[i]["content"],
    });
  }

  CodeService.createHomework(route.params.project_uuid, projectFiles, homework.selectedCourse.id, homework.deadlineDate.toISOString(), homework.computationTime).then(
    (response) => {
      // close modal
      var elem = document.getElementById("createHomeworkModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data) {
        const toast = new Toast(
          document.getElementById("toastHomeworkCreationSuccess")
        );
        toast.show();
      } else {
        const toast = new Toast(
          document.getElementById("toastHomeworkCreationError")
        );
        toast.show();
      }
    }, (error) => {
      // close modal
      var elem = document.getElementById("createHomeworkModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastHomeworkCreationError")
      );
      toast.show();
      console.log(error.response)
    })
}


function prepareHomeworkModal() {
  homework.selectedCourse = {}
  homework.deadlineDate = new Date()
  homework.computationTime = 10

  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new Popover(popoverTriggerEl, { trigger: 'focus', html: true }))
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

      <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateDescriptionError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Speichern der Projektbeschreibung!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateProjectNameError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Speichern des Projektnamens!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateProjectNameTooShort" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Projektname muss mindestens 3 Zeichen lang sein!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastProjectAccessError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Projekt existiert nicht, oder du hast keinen Zugriff darauf!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastHomeworkCreationError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Erstellen der Hausaufgabe!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastHomeworkCreationSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Hausaufgabe erfolgreich erstellt!
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div class="modal fade" id="templateWarningModal" tabindex="-1" aria-labelledby="templateWarningModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Änderung der Vorlage kann zu Inkonsistenzen führen!</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Du bearbeitest gerade die <u>Vorlage</u> einer Hausaufgabe! Wenn du Änderungen am <b>Code</b> durchführst und
            speicherst,
            dann kann dies zu Inkonsistenzen bei den verschiedenen SuS führen:
            <ul>
              <li>Bei SuS, welche diese Hausaufgabe bereits bearbeiten, werden diese Änderungen <b>nicht ankommen</b>,
                solange sie ihren Fortschritt nicht löschen und die HA anschließend neu starten.</li>
              <li>SuS, welche diese Hausaufgabe noch nicht gestartet haben, werden beim erstmaligen Öffnen immer den zu
                diesem Zeitpunkt aktuellsten Code dieser Vorlage verwenden.</li>
            </ul>
            Änderungen des <b>Titels oder der Projektbeschreibung</b> sind hingegen kein Problem, können jederzeit
            geändert werden und werden beim Neuladen der IDE bei den SuS aktualisiert.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Verstanden</button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="createHomeworkModal" tabindex="-1" aria-labelledby="createHomeworkModalLabel"
      aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content dark-text">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Hausaufgabe erstellen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <span>⚠️<b>Wichtig:</b> Die Konfiguration eines Projektes sollte vollständig abgeschlossen sein, <b>bevor</b>
              du daraus eine Hausaufgabe erstellst. Nach diesem Schritt sollten Änderungen vermieden werden, da die
              Schüler/innen andernfalls u. U. unterschiedliche Versionen bearbeiten.</span>
            <hr>
            <div class="mb-3 row">
              <label for="coursename" class="col-sm-4 col-form-label">
                <font-awesome-icon v-if="Object.keys(homework.selectedCourse).length !== 0" icon="fa-square-check"
                  style="color: var(--bs-success)" />
                <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" /> Kurs wählen:</label>
              <div class="col-sm-8 d-flex align-items-center">
                <CourseBadge v-if="homework.selectedCourse" :color="homework.selectedCourse.color"
                  :font-dark="homework.selectedCourse.fontDark" :name="homework.selectedCourse.name" />
                <a class="btn-round btn" data-bs-toggle="dropdown">
                  <font-awesome-layers class="fa-lg" style="display: block !important;">
                    <font-awesome-icon icon="fa-circle" style="color: var(--bs-secondary)" />
                    <div style="color: var(--bs-light)">
                      <font-awesome-icon icon="fa-plus" transform="shrink-6" />
                    </div>
                  </font-awesome-layers>
                </a>
                <ul class="dropdown-menu">
                  <li v-for="c in allCourses">
                    <a class="dropdown-item btn" @click.prevent="homework.selectedCourse = c">
                      <CourseBadge :color="c.color" :font-dark="c.fontDark" :name="c.name" />
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div class="mb-3 row">
              <label for="deadline" class="col-sm-4 col-form-label">
                <font-awesome-icon v-if="homework.deadlineDate > new Date()" icon="fa-square-check"
                  style="color: var(--bs-success)" />
                <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" /> Abgabefrist:</label>
              <div class="col-sm-8">
                <!-- Sadly can't use the option :format-locale="de" because then I can't manually edit the input-field for some reason... -->
                <VueDatePicker v-model="homework.deadlineDate" placeholder="Start Typing ..." text-input auto-apply
                  :min-date="new Date()" prevent-min-max-navigation locale="de" format="E dd.MM.yyyy, HH:mm" />
                UTC: <em>{{ homework.deadlineDate.toISOString() }}</em><br>
                Bearbeitungszeit: <em v-if="homework.deadlineDate > new Date()"><b>{{ Math.floor((homework.deadlineDate -
                  new
                    Date()) / (1000 * 3600 * 24)) }} Tage,
                    {{ Math.floor((homework.deadlineDate - new Date()) / (1000 * 3600) % 24) }} Stunden</b></em>
              </div>
            </div>
            <div class="mb-3 row">
              <label for="deadline" class="col-sm-4 col-form-label">
                <font-awesome-icon
                  v-if="homework.computationTime >= 3 && Number.isInteger(Number(homework.computationTime))"
                  icon="fa-square-check" style="color: var(--bs-success)" />
                <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" /> Rechenzeit:
                <a class="btn-round btn" data-bs-trigger="focus" tabindex="0" data-bs-toggle="popover" title="Rechenzeit"
                  data-bs-content="Lege fest, wie viele <b>Sekunden</b> Rechenzeit (bzw. genauer: Laufzeit) auf dem Server pro Aktion zur Verfügung stehen. Als Aktion gilt:<ul><li>Kompilieren</li><li>Ausführen</li><li>Testen</li></ul>Der Standardwert beträgt 10 Sekunden, welchen Schüler/innen in eigenen Projekten auch <b>nicht</b> verändern können, da der Server mit endlos laufenden Programmen lahm gelegt werden könnte. Unter Umständen kann es aber sinnvoll sein, bei Hausaufgaben die Laufzeit zu verlängern, z. B. wenn ein Programm auf Benutzereingaben warten muss, welche auch ihre Zeit brauchen.">
                  <font-awesome-icon icon="fa-circle-question" size="lg" style="color: var(--bs-primary)" />
                </a></label>
              <div class="col-sm-8">
                <input :value="homework.computationTime" @input="event => homework.computationTime = event.target.value"
                  type="number" min="3" step="1" placeholder="Mindestens 3, Standard 10" />
                <br>
                {{ homework.computationTime }} Sekunden
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
            <button type="button" class="btn btn-primary" @click.prevent="createHomework()"
              :disabled="Object.keys(homework.selectedCourse).length === 0 || homework.deadlineDate <= new Date() || !(homework.computationTime >= 3 && Number.isInteger(Number(homework.computationTime)))">Hausaufgabe
              erstellen</button>
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
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
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
                  <a class="dropdown-item" href="#"><font-awesome-icon icon="fa-solid fa-xmark" /> Projekt
                    schließen</a>
                </li>
              </ul>
            </li>
            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button @click.prevent="undo()" type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-left-long" />
              </button>
              <button @click.prevent="redo()" type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-rotate-right" />
              </button>
            </div>

            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button @click.prevent="saveAll()" type="button" class="btn btn-green"
                :disabled="state.tabsWithChanges.length == 0">
                <div v-if="state.isSaving" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-floppy-disk" />
                Speichern
              </button>
              <button @click.prevent="compile()" type="button" class="btn btn-yellow">
                <div v-if="state.isCompiling" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid btn-yellow fa-gear" />
                Kompilieren
              </button>
              <button @click.prevent="execute()" type="button" class="btn btn-blue">
                <div v-if="state.isExecuting" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-circle-play" />
                Ausführen
              </button>
              <button v-if="authStore.isTeacher() || state.isHomework" @click.prevent="test()" type="button"
                class="btn btn-indigo">
                <div v-if="state.isTesting" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-list-check" /> Testen
              </button>
            </div>
            <button v-if="authStore.isTeacher() && !state.isHomework" @click.prevent="prepareHomeworkModal()"
              type="button" data-bs-toggle="modal" data-bs-target="#createHomeworkModal" class="btn btn-outline-info">
              <font-awesome-icon icon="fa-solid fa-share-nodes" /> Hausaufgabe erstellen
            </button>
            <div class="d-flex align-items-center homework-badge px-2" v-if="state.isHomework">HA | <span
                v-if="authStore.isTeacher() && route.params.user_id == 0">Vorlage</span><span
                v-else-if="authStore.isTeacher() && route.params.user_id != 0">{{ state.fullUserName }}</span><span
                v-else-if="!authStore.isTeacher()">Abgabe: {{ new
                  Date(state.deadline).toLocaleString("default", {
                    weekday: "long", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"
                  }) }}</span></div>
          </ul>
        </div>
      </div>
    </nav>

    <div class="ide-main">
      <splitpanes class="default-theme" height="100%" horizontal :push-other-panes="false">
        <pane>
          <splitpanes :push-other-panes="false">
            <pane min-size="15" size="20" max-size="30">
              <splitpanes class="default-theme" horizontal :push-other-panes="false">
                <pane style="background-color: #383838">
                  <div class="projectName d-flex align-items-center justify-content-center position-relative">
                    <p class="placeholder-wave" v-if="state.projectName === ''">
                      <span class="placeholder col-12"></span>
                    </p>
                    <div v-else>
                      <div v-if="!state.editingProjectName">
                        <span>{{ state.projectName }}</span>
                        <div v-if="route.params.user_id == 0"
                          class="position-absolute top-50 end-0 mx-1 translate-middle-y">
                          <a @click.prevent="editProjectName()" class="btn btn-overlay btn-outline-secondary">
                            <div>
                              <font-awesome-icon icon="fa-pencil" />
                            </div>
                          </a>
                        </div>
                      </div>
                    </div>
                    <div v-if="state.editingProjectName" class="flex-fill">
                      <div class="align-items-center d-flex flex-row">
                        <input class="rounded flex-fill" type="text" id="inputMessage" v-model="state.newProjectName" />
                        <a @click.prevent="abortProjectName()" class="btn btn-overlay btn-abort mx-1">
                          <div>
                            <font-awesome-icon icon="fa-solid fa-times" />
                          </div>
                        </a>
                        <a @click.prevent="saveProjectName()" class="btn btn-overlay btn-edit">
                          <div v-if="state.isSavingProjectName" class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                          </div>
                          <div v-else>
                            <font-awesome-icon icon="fa-solid fa-check" />
                          </div>
                        </a>
                      </div>
                    </div>
                  </div>
                  <IDEFileTree :files="state.files" @openFile="openFile" />
                </pane>
                <!-- Description -->
                <pane min-size="10" size="50" max-size="60" style="background-color: #383838">
                  <div v-if="!state.editingDescription" class="position-relative description">
                    <span>
                      {{ state.projectDescription }}
                    </span>
                    <div v-if="route.params.user_id == 0" class="position-absolute bottom-0 end-0">
                      <a @click.prevent="editDescription()" class="btn btn-overlay btn-outline-secondary">
                        <div>
                          <font-awesome-icon icon="fa-pencil" />
                        </div>
                      </a>
                    </div>
                  </div>
                  <div v-if="state.editingDescription" class="position-relative edit-description">
                    <textarea class="textarea-description" v-model="state.newProjectDescription" />
                    <div class="position-absolute bottom-0 end-0">
                      <a @click.prevent="abortDescription()" class="btn btn-overlay btn-abort">
                        <div>
                          <font-awesome-icon icon="fa-xmark" fixed-width />
                        </div>
                      </a>
                      <a @click.prevent="saveDescription()" class="btn btn-overlay btn-edit">
                        <div>
                          <div v-if="state.isSavingDescription" class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                          </div>
                          <font-awesome-icon v-else icon="fa-check" fixed-width />
                        </div>
                      </a>
                    </div>
                  </div>

                </pane>

              </splitpanes>
            </pane>
            <pane>
              <ul class="nav nav-tabs pt-2">
                <li class="nav-item" v-for="f in state.openFiles">
                  <div class="nav-link tab" @click.prevent="openFile(f.path)" :id="'fileTab' + f.tab" :class="{
                      active: f.tab == state.activeTab,
                      changed: state.tabsWithChanges.includes(f.tab),
                    }">
                    {{ f.path }}
                  </div>
                </li>
              </ul>
              <v-ace-editor id="editor" value="" @init="editorInit" lang="java" theme="monokai" />
            </pane>

          </splitpanes>
        </pane>
        <pane size="20" max-size="50">
          <div class="bottom d-flex flex-column">
            <div class="output p-2 flex-grow-1" id="output">
              <pre>{{ results }}</pre>
            </div>
            <div class="input align-items-center d-flex flex-row">
              <label for="inputMessage" class="px-2 col-form-label">Eingabe:</label>
              <!-- <div> -->
              <input class="rounded flex-fill" :disabled="!state.websocket_open" @keyup.enter="sendMessage()" type="text"
                id="inputMessage" v-model="state.sendMessage" placeholder="Eingabe (Entertaste zum Senden)" />
              <!-- </div> -->
              <button :disabled="!state.websocket_open" @click.prevent="sendMessage()" type="button"
                class="btn btn-light btn-sm mx-2" id="messageSendButton">
                Senden
              </button>
            </div>
          </div>
        </pane>
      </splitpanes>
    </div>
  </div>
</template>

<style scoped>
#inputMessage:disabled {
  background-color: white;
}

#messageSendButton {
  transition: 0.4s;
}

.homework-badge {
  border: 1px solid #666;
  color: #999;
  border-radius: 7px;
  white-space: pre;
}

.btn-round {
  padding: 0;
  border: 0px;
}

.dark-text {
  color: var(--bs-dark);
}

.edit-description {
  height: 100%;
}

.textarea-description {
  height: 100%;
  width: 100%;
}

.btn-abort {
  background-color: lightcoral !important;
  color: black !important;
}

.btn-edit {
  background-color: lightgreen !important;
  color: black !important;
}

.btn-overlay:hover {
  box-shadow: inset 0 0 30px 30px rgba(150, 150, 150, 0.7);
  ;
}

.description {
  white-space: pre-line;
  overflow-y: auto;
  display: block;
  height: 100%;
}

.bottom {
  width: 100%;
  height: 100%;
  background-color: #383838;
}

.input {
  border-top: 1px solid #ccc;
}

.output {
  width: 100%;
  /* height: 100%; */
  background-color: #383838;
  font-family: "Courier New", Courier, monospace;
  overflow-y: auto;
}

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
  height: 50px;
  border-bottom: 1px solid #555;
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
