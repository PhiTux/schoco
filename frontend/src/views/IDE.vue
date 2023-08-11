<script setup>
import { onBeforeMount, onBeforeUnmount, reactive, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Toast, Popover, Modal, Tooltip } from "bootstrap";
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
import "ace-builds/src-min-noconflict/theme-xcode";
import "ace-builds/src-min-noconflict/ext-language_tools";
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import ColorModeSwitch from "../components/ColorModeSwitch.vue";
import { debounce } from "lodash";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const ZOOMMIN = 12
const ZOOMMAX = 28

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
  websocket_working: true,
  renameFilePath: "",
  renameFileNewName: "",
  isRenamingFile: false,
  editorZoom: 16,
  closeTabAfterSaving: false,
  closeIDEAfterSaving: false,
  closeTabID: 0,
  actionGoal: "",
  newFileName: "",
  isAddingFile: false,
  newFileNameInvalid: false,
  deleteFilePath: "",
  isDeletingFile: false,
  isResettingHomework: false,
  isCreatingHomework: false,
  runningContainerUuid: "",
  aborted: false,
  isStopping: false,
});

let homework = reactive({
  deadlineDate: new Date(),
  selectedCourse: "",
  computationTime: "",
  id: 0,
})

let allCourses = ref([])

/** Stores the output displayed in the bottom pane. */
let results = ref("");
let resultsElement = ref(null);

let ws;

var isMac = /mac/i.test(navigator.userAgentData ? navigator.userAgentData.platform : navigator.platform);


function scrollResults() {
  let output = document.getElementById("output");
  output.scrollTop = output.scrollHeight;
}


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
  ace.require("ace/ext/language_tools");
  var editor = ace.edit("editor");
  editor.setOptions({
    tabSize: 4,
    useSoftTabs: true,
    navigateWithinSoftTabs: true,
    fontSize: 16,
    scrollPastEnd: 0.5,
    enableBasicAutocompletion: true,
    showPrintMargin: false,
    autoScrollEditorIntoView: true,
  });
  editor.on("change", editorChange);
}

function checkKeyDown(e) {
  if (isMac ? e.metaKey : e.ctrlKey) {
    if (e.key === 's') {
      e.preventDefault()
      saveAllBtn()
    } else if (e.key === '+') {
      e.preventDefault()
      zoomPlus()
    } else if (e.key === '-') {
      e.preventDefault()
      zoomMinus()
    } else if (e.key === '1') {
      e.preventDefault()
      compileBtn()
    } else if (e.key === '2') {
      e.preventDefault()
      executeBtn()
    } else if (e.key === '3') {
      e.preventDefault()
      testBtn()
    }
  }
}

onBeforeMount(() => {
  window.addEventListener('keydown', checkKeyDown)

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
  )


  CodeService.getProjectInfo(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.status == 200) {
        state.isHomework = response.data.isHomework;
        state.projectName = response.data.name;
        state.projectDescription = response.data.description;
        if (state.isHomework) {
          state.fullUserName = response.data.fullusername;
          state.deadline = response.data.deadline
          homework.id = response.data.id

          // show warning about editing the template
          if (route.params.user_id == 0) {
            var modal = new Modal(document.getElementById('templateWarningModal'));
            modal.show();
          }
        }
      }

      document.title = state.projectName
    },
    (error) => {
      console.log(error);
      document.title = "Projekt"
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

onBeforeUnmount(() => {
  // remove event listener
  window.removeEventListener('keydown', checkKeyDown)
});

let worker
onMounted(async () => {
  //set light/dark mode of editor
  if (localStorage.getItem("theme") == "light") {
    setLight(true)
  } else if (localStorage.getItem("theme") == "dark") {
    setLight(false)
  } else {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setLight(false)
    } else {
      setLight(true)
    }
  }

  // enable websocket-worker (other thread for decoding)
  worker = new Worker(new URL("../services/websocket-worker.js", import.meta.url), { type: "module" });

  // observe the HTML-Element to trigger scrolling to bottom of results
  const observer = new MutationObserver(async () => {
    scrollResults()
  });
  observer.observe(resultsElement.value, { childList: true });

  // enable tooltips (wait until test-button is rendered after getProjectInfo())
  setTimeout(() => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl))
  }, 500)

})

function setLight(light) {
  if (document.getElementById('editor') == null) return

  let editor = ace.edit("editor");
  if (light) {
    editor.setTheme('ace/theme/xcode')
  } else {
    editor.setTheme('ace/theme/monokai')
  }
}

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

function saveAllBtn() {
  state.actionGoal = "";
  saveAll()
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

      if (state.actionGoal !== "") {
        compile()
      }

      if (state.closeIDEAfterSaving) {
        exit();
        return;
      } else if (state.closeTabAfterSaving) {
        closeTab(state.closeTabID)
      }
    },
    (error) => {
      // toast error
      const toast = new Toast(
        document.getElementById("toastSavingError")
      );
      toast.show();

      state.isSaving = false;
      state.actionGoal = "";

      console.log(error);
    }
  );
}

function compileBtn() {
  state.actionGoal = "compile"
  compile()
}

function compile() {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  // if something to save, then first save
  if (state.tabsWithChanges.length) {
    saveAll()
    return
  }

  state.isCompiling = true;
  state.aborted = false;
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

      state.runningContainerUuid = response.data.uuid;

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
      state.actionGoal = ""
      console.log(error.response);
    }
  );
}

function startCompile(ip, port, container_uuid, project_uuid, user_id) {
  CodeService.startCompile(ip, port, container_uuid, project_uuid, user_id, !state.websocket_working).then(
    (response) => {
      state.isCompiling = false;

      if (state.actionGoal === "compile" || (state.websocket_working && state.receivedWS)) {
        state.actionGoal = ""
      }

      if (response.data.status === "connect_error") {
        results.value =
          'Interner Verbindungsfehler ⚡ Vermutlich war der "Worker" (Teil des Servers, der u. a. kompiliert) einfach noch nicht soweit... \nBitte direkt erneut probieren 😊';
        state.actionGoal = ""
        return;
      }
      else if (!state.websocket_working || response.data.stdout !== undefined) {
        if (response.data.stdout === undefined) {
          // restart compilation if from this last run no output was saved
          compile()
          return;
        } else if (response.data.exitCode == 0 && (response.data.stdout === "" || response.data.stdout === "\n")) {
          results.value = "Erfolgreich kompiliert 🎉";
        } else {
          results.value = response.data.stdout;
          return;
        }
      }
      else if (response.data.exitCode == 0 && !state.receivedWS) {
        results.value = "Erfolgreich kompiliert 🎉";
      }

      if (state.actionGoal === "execute") {
        execute(true)
      } else if (state.actionGoal === "test") {
        test(true)
      }
    },
    (error) => {
      state.isCompiling = false;
      state.actionGoal = ""

      console.log(error.response);
    }
  );
}


// debouce-function to actually update the results
let buffer = "";
let updateResults = debounce(() => {
  results.value = buffer
  scrollResults()
}, 20, { leading: true })


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

  buffer = "";

  // "outsource" the decoding to web-worker
  ws.onmessage = function (event) {
    worker.postMessage(event.data);
  };

  worker.onmessage = function (event) {
    const msg = event.data;

    if (state.receivedWS == false) {
      state.receivedWS = true;
      results.value = "";
    }

    //check if message is actually the one being sent
    if (msg !== "\r\n" && msg.trim() === state.sendMessage.trim()) {
      state.sendMessage = ""
      return
    }

    buffer = buffer.concat(msg);

    //update results via debounce -> don't do instant updates of "millions" single-lines, but rather update every few ms
    updateResults()
  };

  ws.onerror = function (event) {
    state.websocket_open = false;
    state.websocket_working = false;
    if (state.isCompiling || state.isExecuting || state.isTesting) {
      results.value = "Live-Ausgabe nicht möglich, Ergebnis folgt gleich..."
    }
  };

  ws.onopen = function (event) {
    state.websocket_open = true;
    state.websocket_working = true;
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

function executeBtn() {
  state.actionGoal = "execute"
  execute(false)
}

function execute(just_compiled) {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  if (!just_compiled && state.tabsWithChanges.length) {
    saveAll()
    return
  }

  state.isExecuting = true;
  state.aborted = false;
  state.receivedWS = false;

  results.value = "";

  CodeService.prepareExecute(route.params.project_uuid, route.params.user_id).then(
    async (response) => {
      if (response.data.executable == false) {
        results.value =
          "🔎 Leider keine ausführbaren Dateien gefunden. Bitte zuerst kompilieren ⚙";
        state.isExecuting = false;
        compile()
        return;
      }

      state.runningContainerUuid = response.data.uuid;

      connectWebsocket(response.data.id);

      // wait max. 250ms for websocket to open
      await new Promise((resolve) => {
        let timer = 0;
        const intervalId = setInterval(() => {
          if (state.websocket_open) {
            clearInterval(intervalId);
            resolve();
          } else if (timer >= 250) {
            state.websocket_working = false;
            clearInterval(intervalId);
            resolve();
          }
          timer += 50;
        }, 50);
      });

      startExecute(
        response.data.ip,
        response.data.port,
        response.data.uuid,
        route.params.project_uuid,
        route.params.user_id
      );
    },
    (error) => {
      state.actionGoal = ""

      state.isExecuting = false;
      console.log(error.response);
    }
  );
}

function startExecute(ip, port, uuid, project_uuid, user_id) {
  CodeService.startExecute(ip, port, uuid, project_uuid, user_id, !state.websocket_working).then(
    (response) => {

      state.isExecuting = false;
      state.actionGoal = ""

      if (state.websocket_working && state.receivedWS == false) {
        results.value = "Programm wurde (erfolgreich, aber ohne Ausgabe) beendet! ✔";
      }

      if (response.data.status === "connect_error") {
        if (!state.aborted) {
          results.value =
            'Interner Verbindungsfehler ⚡ Vermutlich war der "Worker" (Teil des Servers, der u. a. kompiliert) einfach noch nicht soweit... \nBitte direkt erneut probieren 😊';
        }

        state.actionGoal = ""
        return;
      }
      else if (!state.websocket_working || response.data.stdout !== undefined) {
        if (response.data.stdout === undefined) {
          // restart execution if from this last run no output was saved
          execute()
          return;
        } else if (response.data.exitCode == 0 && (response.data.stdout === "" || response.data.stdout === "\n")) {
          results.value = "Programm wurde (erfolgreich, aber ohne Ausgabe) beendet! ✔";
        } else {
          results.value = response.data.stdout;
          return;
        }
      }

    },
    (error) => {
      if (state.receivedWS == false) {
        results.value = "Programm wurde (vermutlich fehlerhaft) beendet! ❌";
      }
      state.isExecuting = false;
      state.actionGoal = ""
      console.log(error.response);
    }
  );
}

function testBtn() {
  if (!authStore.isTeacher() && !state.isHomework) return;

  state.actionGoal = "test"
  test(false)
}

function test(just_compiled) {
  if (state.isSaving || state.isCompiling || state.isExecuting || state.isTesting) return;

  if (!just_compiled && state.tabsWithChanges.length) {
    saveAll()
    return
  }

  state.isTesting = true;
  state.aborted = false;
  state.receivedWS = false;

  // using this line here (instead at opening WS), since Testing does not start a WS-connection
  results.value = "Programm wird getestet 📝➡️✅ bitte warten..."

  CodeService.prepareTest(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      if (response.data.executable == false) {
        results.value =
          "🔎 Leider keine ausführbaren Dateien gefunden. Bitte zuerst kompilieren ⚙";
        state.isTesting = false;
        compile();
        return;
      }

      state.runningContainerUuid = response.data.uuid;

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
      state.actionGoal = "";
      console.log(error.response);
    }
  );
}


function startTest(ip, port, uuid, project_uuid, user_id) {
  CodeService.startTest(ip, port, uuid, project_uuid, user_id).then(
    (response) => {
      state.isTesting = false;
      state.actionGoal = "";

      results.value = ""

      if (response.data.status === "security_error") {
        results.value = "💥🙈 es gab wohl einen Sicherheitsfehler beim Testen deines Programms. Scheinbar hat dein Programm versucht, Dinge auszuführen, die nicht erlaubt sind. Korrigiere dies zuerst.\nWenn das Problem bestehen bleibt, solltest du dich an deine Lehrerin / deinen Lehrer wenden."
        return
      }

      results.value += response.data.stdout

      results.value += "\n\n==================\n\n"

      if (response.data.exitCode == 143) {
        results.value += "❌ Programm wurde frühzeitig beendet! Die Rechenzeit ist vermutlich abgelaufen. Hast du irgendwo eine Endlosschleife?"
      }
      else if (response.data.failed_tests == 0 && response.data.passed_tests > 0) {
        results.value += "Alle Tests bestanden 🎉🤩\n\nDu kannst nun höchstens noch versuchen, deinen Quellcode zu \"verschönern\" ;-)"
      } else if (response.data.passed_tests == 0) {
        results.value += "Ups 🧐 Scheinbar wurde kein einziger Test bestanden! Vielleicht hilft dir die obere Ausgabe, um den Fehlern auf die Schliche zu kommen 🤗"
      } else if (response.data.passed_tests == 0 && response.data.failed_tests == 0) {
        results.value += "❌ Es gab beim Testen wohl irgendeinen Fehler. Überprüfe nochmals dein Programm."
      } else if (state.aborted) {
        results.value += "❌ Der Test wurde durch den User abgebrochen."
      }
      else {
        let percent = Math.round((response.data.passed_tests / (response.data.passed_tests + response.data.failed_tests)) * 100 * 10) / 10
        results.value += `Du hast ${percent}% der Tests bestanden. Vielleicht hilft dir die obere Ausgabe, um die restlichen Tests auch noch zu bestehen 🤗`
      }

    },
    (error) => {
      results.value = "💥🙈 es gab wohl einen Fehler beim Testen deines Programms. Probiere es erneut!\nStelle zunächst sicher, dass dein Programm ausgeführt werden kann.\nWenn das Problem bestehen bleibt, solltest du dich an deine Lehrerin / deinen Lehrer wenden."
      state.isTesting = false;
      state.actionGoal = "";
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

  if (state.newProjectName.trim() === "") {
    const toast = new Toast(
      document.getElementById("toastUpdateProjectNameEmpty")
    );
    toast.show();
    state.isSavingProjectName = false;
    return;
  }

  CodeService.updateProjectName(route.params.project_uuid, route.params.user_id, state.newProjectName.trim()).then(
    (response) => {
      if (response.data) {
        state.projectName = state.newProjectName.trim();
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
          document.getElementById("toastUpdateProjectNameEmpty")
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
  if (state.isCreatingHomework) return;
  state.isCreatingHomework = true;

  let projectFiles = [];
  for (let i = 0; i < state.files.length; i++) {
    projectFiles.push({
      path: state.files[i]["path"],
      content: state.files[i]["content"],
    });
  }

  CodeService.createHomework(route.params.project_uuid, projectFiles, homework.selectedCourse.id, homework.deadlineDate.toISOString(), homework.computationTime).then(
    (response) => {
      state.isCreatingHomework = false;

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
      state.isCreatingHomework = false;

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
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new Popover(popoverTriggerEl, { html: true }))
}


function renameDirectoryModal() {
  // show modal
  var modal = new Modal(document.getElementById("renameDirectoryModal"));
  modal.show();
}


function deleteDirectoryModal() {
  // show modal
  var modal = new Modal(document.getElementById("deleteDirectoryModal"));
  modal.show();
}


function renameFileModal(path) {
  state.renameFilePath = String(path).replace(/\/$/g, "")
  state.renameFileNewName = ""
  state.newFileNameInvalid = false

  var modal = new Modal(document.getElementById("renameFileModal"));
  modal.show();

  document.getElementById('renameFileModal').addEventListener('shown.bs.modal', function () {
    document.getElementById("renameFilenameInput").focus();
  })
}

function renameFile() {

  if (state.renameFileNewName.trim() === "" || state.renameFileNewName.trim().includes(" ")) {
    state.newFileNameInvalid = true
    return;
  }

  state.isRenamingFile = true;

  // get file content and sha
  let fileContent = ""
  let sha = ""
  for (let i = 0; i < state.files.length; i++) {
    if (state.files[i]["path"] === state.renameFilePath) {
      fileContent = state.files[i]["content"]
      sha = state.files[i]["sha"]
      break
    }
  }

  CodeService.renameFile(route.params.project_uuid, route.params.user_id, state.renameFilePath, state.renameFileNewName, fileContent, sha).then(
    (response) => {
      state.isRenamingFile = false;

      // close modal
      var elem = document.getElementById("renameFileModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      if (response.data.success) {
        const toast = new Toast(
          document.getElementById("toastRenameFileSuccess")
        );
        toast.show();

        //update file list
        for (let i = 0; i < state.files.length; i++) {
          if (state.files[i]["path"] === state.renameFilePath) {
            state.files[i]["path"] = state.renameFileNewName
            break
          }
        }

        // update open file list
        for (let i = 0; i < state.openFiles.length; i++) {
          if (state.openFiles[i]["path"] === state.renameFilePath) {
            state.openFiles[i]["path"] = state.renameFileNewName
            break
          }
        }

      } else {
        const toast = new Toast(
          document.getElementById("toastRenameFileError")
        );
        toast.show();
      }

      state.renameFilePath = ""
      state.renameFileNewName = ""
    }, (error) => {
      state.isRenamingFile = false;

      // close modal
      var elem = document.getElementById("renameFileModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      const toast = new Toast(
        document.getElementById("toastRenameFileError")
      );
      toast.show();
      console.log(error.response)

      state.renameFilePath = ""
      state.renameFileNewName = ""
    })
}

function checkExit() {
  if (state.tabsWithChanges.length) {
    state.closeIDEAfterSaving = true

    // open Modal
    var modal = new Modal(document.getElementById("saveBeforeCloseModal"));
    modal.show();
  } else {
    exit()
  }
}

function exit() {

  // if (pupil) OR (teacher and !homework): go to /home
  if (!authStore.isTeacher() || (authStore.isTeacher() && !state.isHomework)) {
    router.push({
      name: "home"
    });
  } else { // else: teacher viewing homework
    router.go(-1)
  }
}

/* 🛑 This function also exists at ./Home.vue 🛑 */
function downloadProject(uuid) {
  CodeService.downloadProject(uuid).then(
    (response) => {
      let filename = response.headers["content-disposition"].split("filename=")[1]

      let fileUrl = window.URL.createObjectURL(response.data);
      let fileLink = document.createElement('a');

      fileLink.href = fileUrl;
      fileLink.setAttribute('download', filename);
      document.body.appendChild(fileLink)

      fileLink.click();

      // remove link from DOM
      document.body.removeChild(fileLink)
    },
    error => {
      console.log(error.response)
      const toast = new Toast(
        document.getElementById("toastDownloadProjectError")
      );
      toast.show();
    }
  )
}

function zoom(zoom) {
  let newZoom
  if (zoom < ZOOMMIN) {
    newZoom = ZOOMMIN
  } else if (zoom > ZOOMMAX) {
    newZoom = ZOOMMAX
  } else {
    newZoom = zoom
  }

  state.editorZoom = parseInt(newZoom)
  document.getElementById('editor').style.fontSize = newZoom + 'px';
}

function zoomPlus() {
  if (state.editorZoom + 1 <= ZOOMMAX) {
    state.editorZoom++;
    zoom(state.editorZoom)
  }
}

function zoomMinus() {
  if (state.editorZoom - 1 >= ZOOMMIN) {
    state.editorZoom--;
    zoom(state.editorZoom)
  }
}

function checkCloseTab(tabID) {
  console.log(tabID)

  if (state.tabsWithChanges.includes(tabID)) {
    state.closeTabID = tabID
    state.closeTabAfterSaving = true

    // open Modal
    var modal = new Modal(document.getElementById("saveBeforeCloseModal"));
    modal.show();
  } else {
    closeTab(tabID)
  }
}

function closeTab(tabID) {
  // remove from tabsWithChanges
  for (let i = 0; i < state.tabsWithChanges.length; i++) {
    if (state.tabsWithChanges[i] === tabID) {
      state.tabsWithChanges.splice(i, 1)
      break;
    }
  }

  for (let i = 0; i < state.openFiles.length; i++) {
    if (state.openFiles[i].tab === tabID) {
      state.openFiles.splice(i, 1);

      // open first tab
      openFile(state.openFiles[0].path)
      break;
    }
  }
}

function prepareAddFileModal() {
  state.newFileName = ""
  state.isAddingFile = false
  state.newFileNameInvalid = false

  var modal = new Modal(document.getElementById("addFileModal"));
  modal.show();

  document.getElementById('addFileModal').addEventListener('shown.bs.modal', function () {
    document.getElementById("addFilenameInput").focus();
  })
}

function addFile() {
  if (state.isAddingFile) return;

  if (state.newFileName.trim() === "" || state.newFileName.trim().includes(" ")) {
    state.newFileNameInvalid = true
    return;
  }

  state.isAddingFile = true

  CodeService.addEmptyFile(route.params.project_uuid, route.params.user_id, state.newFileName.trim()).then(
    (response) => {
      state.isAddingFile = false

      if (response.data.success) {
        // add to file list
        state.files.push({
          path: state.newFileName.trim(),
          content: "",
          sha: response.data.sha
        })

        // close modal
        var elem = document.getElementById("addFileModal");
        var modal = Modal.getInstance(elem);
        modal.hide();

        // show toast
        const toast = new Toast(
          document.getElementById("toastAddFileSuccess")
        );
        toast.show();

      } else if (response.data.error === "filename_invalid") {
        state.newFileNameInvalid = true
      } else {
        // close modal
        var elem = document.getElementById("addFileModal");
        var modal = Modal.getInstance(elem);
        modal.hide();

        // show error toast
        const toast = new Toast(
          document.getElementById("toastAddFileError")
        );
        toast.show();
      }
    }, (error) => {
      state.isAddingFile = false
      console.log(error.response)

      // close modal
      var elem = document.getElementById("addFileModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      // show error toast
      const toast = new Toast(
        document.getElementById("toastAddFileError")
      );
      toast.show();
    })
}

function deleteFileModal(path) {
  console.log(path)
  state.deleteFilePath = String(path).replace(/\/$/g, "")

  var modal = new Modal(document.getElementById("deleteFileModal"));
  modal.show();
}

function deleteFile() {
  if (state.isDeletingFile) return;

  state.isDeletingFile = true

  // get sha from files
  let sha = ""
  for (let i = 0; i < state.files.length; i++) {
    if (state.files[i]["path"] === state.deleteFilePath) {
      sha = state.files[i]["sha"]
      break
    }
  }

  CodeService.deleteFile(route.params.project_uuid, route.params.user_id, state.deleteFilePath, sha).then(
    (response) => {
      state.isDeletingFile = false

      if (response.data.success) {

        // remove from open file list
        for (let i = 0; i < state.openFiles.length; i++) {
          if (state.openFiles[i]["path"] === state.deleteFilePath) {
            // remove from tabsWithChanges
            for (let x = 0; x < state.tabsWithChanges.length; x++) {
              if (state.tabsWithChanges[x] === state.openFiles[i]["tab"]) {
                state.tabsWithChanges.splice(x, 1)
                break;
              }
            }

            state.openFiles.splice(i, 1)

            // open first tab
            openFile(state.openFiles[0].path)

            break
          }
        }

        // remove from file list
        for (let i = 0; i < state.files.length; i++) {
          if (state.files[i]["path"] === state.deleteFilePath) {
            state.files.splice(i, 1)
            break
          }
        }

        // close modal
        var elem = document.getElementById("deleteFileModal");
        var modal = Modal.getInstance(elem);
        modal.hide();
      } else {
        // close modal
        var elem = document.getElementById("deleteFileModal");
        var modal = Modal.getInstance(elem);
        modal.hide();

        // show error toast
        const toast = new Toast(
          document.getElementById("toastDeleteFileError")
        );
        toast.show();
      }
    }, (error) => {
      state.isDeletingFile = false
      console.log(error.response)

      // close modal
      var elem = document.getElementById("deleteFileModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      // show error toast
      const toast = new Toast(
        document.getElementById("toastDeleteFileError")
      );
      toast.show();
    })
}

function prepareDeleteHomework() {
  state.isResettingHomework = false

  var modal = new Modal(document.getElementById("restartHomeworkBranchModal"));
  modal.show();
}

function deleteHomework() {
  if (state.isResettingHomework || !state.isHomework) return;

  state.isResettingHomework = true

  CodeService.deleteProject(route.params.project_uuid, route.params.user_id).then(
    (response) => {
      state.isResettingHomework = false

      if (response.data) {
        // reload site
        CodeService.startHomework(homework.id).then(
          (response) => {
            if (response.data) {
              // close modal
              var elem = document.getElementById("restartHomeworkBranchModal");
              var modal = Modal.getInstance(elem);
              modal.hide();

              router.go(0);
            } else {
              // show error toast
              const toast = new Toast(
                document.getElementById("toastDeleteProjectError")
              );
              toast.show();
            }
          }, (error) => {
            console.log(error.response)
          }
        )
      } else {
        // close modal
        var elem = document.getElementById("restartHomeworkBranchModal");
        var modal = Modal.getInstance(elem);
        modal.hide();

        // show error toast
        const toast = new Toast(
          document.getElementById("toastDeleteProjectError")
        );
        toast.show();
      }
    }, (error) => {
      state.isResettingHomework = false
      console.log(error.response)

      // close modal
      var elem = document.getElementById("restartHomeworkBranchModal");
      var modal = Modal.getInstance(elem);
      modal.hide();

      // show error toast
      const toast = new Toast(
        document.getElementById("toastDeleteProjectError")
      );
      toast.show();
    })
}


function stopContainer() {
  if (state.aborted || state.runningContainerUuid === "" || (!state.isExecuting && !state.isTesting)) return;

  state.aborted = true;
  state.isStopping = true;

  CodeService.stopContainer(state.runningContainerUuid).then(
    (response) => {
      state.isStopping = false;

      if (response.data.success) {
        results.value += "\nProgramm wurde vom User beendet! ✔";
      } else {
        // show toast
        const toast = new Toast(
          document.getElementById("toastStopContainerError")
        );
        toast.show();
      }
    }, (error) => {
      // show toast
      const toast = new Toast(
        document.getElementById("toastStopContainerError")
      );
      toast.show();
      console.log(error.response)
    })
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

      <div class="toast align-items-center text-bg-danger border-0" id="toastDownloadProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Download des Projekts.
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastSavingError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Speichern!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastRenameFileError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Datei konnte nicht umbenannt werden!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-success border-0" id="toastRenameFileSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Datei erfolgreich umbenannt!
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

      <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateProjectNameEmpty" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Projektname darf nicht leer sein!
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

      <div class="toast align-items-center text-bg-success border-0" id="toastAddFileSuccess" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Datei erfolgreich erstellt!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastAddFileError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Erstellen der Datei!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteFileError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Löschen der Datei!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastDeleteProjectError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Fehler beim Zurücksetzen der Hausaufgabe!
          </div>
        </div>
      </div>

      <div class="toast align-items-center text-bg-danger border-0" id="toastStopContainerError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            Programm konnte nicht beendet werden!
          </div>
        </div>
      </div>
    </div>


    <!-- Modals -->
    <div class="modal fade" id="templateWarningModal" tabindex="-1" aria-labelledby="templateWarningModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Änderung der Vorlage kann zu Inkonsistenzen führen!</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Du bearbeitest gerade die <u>Vorlage</u> einer Hausaufgabe! Wenn du Änderungen am <b>Code</b> durchführst
            und
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

    <div class="modal fade" id="saveBeforeCloseModal" tabindex="-1" aria-labelledby="saveBeforeCloseModalLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Änderungen speichern?</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Möchtest du die Änderungen vor dem Schließen speichern?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"
              @click.prevent="state.closeIDEAfterSaving ? exit() : (state.closeTabAfterSaving && closeTab(state.closeTabID))">Nicht
              speichern</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click.prevent="saveAllBtn()">
              Speichern
            </button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="addFileModal" tabindex="-1" aria-labelledby="addFileLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Neue Datei hinzufügen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Gib den neuen Dateinamen für die Datei ein. Denke an die Dateiendung
            (typischerweise <code>.java</code>)! <br> <br>
            Wenn du einen Order anlegen möchtest, dann musst du gleichzeitig auch eine Datei innerhalb des neuen Ordners
            angeben. <br>
            <br>
            <b><u>Beispiel:</u></b><br>
            Wenn du den Ordner "<code>neu</code>" anlegen möchtest, dann musst du auch eine Datei innerhalb des Ordners
            angeben (z. B. <code>MeineKlasse.java</code>). Gib daher als vollen Dateinamen
            <code>neu/MeineKlasse.java</code> an.


            <div class="input-group my-3">
              <input type="text" class="form-control" id="addFilenameInput" v-model="state.newFileName"
                @keyup.enter="addFile()">
            </div>

            <div v-if="state.newFileNameInvalid" class="alert alert-danger" role="alert">
              Dateiname ist ungültig (enthält Leerzeichen oder der Name existiert bereits)!
            </div>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
            <button type="button" class="btn btn-primary" @click.prevent="addFile()">
              <span v-if="!state.isAddingFile">Hinzufügen</span>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="deleteFileModal" tabindex="-1" aria-labelledby="deleteFileLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Datei löschen?</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Möchtest du die Datei <b><u>{{ state.deleteFilePath }}</u></b> wirklich löschen?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
            <button type="button" class="btn btn-primary" @click.prevent="deleteFile()">
              <span v-if="!state.isDeletingFile">Löschen</span>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="deleteDirectoryModal" tabindex="-1" aria-labelledby="deleteDirectoryLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Ordner löschen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Ordner können leider <b>nicht</b> direkt gelöscht werden. Du kannst allerdings sämtlichen Inhalt des
            Ordners löschen, dann wird der Ordner automatisch mitgelöscht.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Verstanden</button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="renameDirectoryModal" tabindex="-1" aria-labelledby="renameDirectoryLabel"
      aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Ordner umbenennen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Ordner können leider <b>nicht</b> direkt umbenannt werden. Du kannst allerdings sämtlichen Inhalt
            des Ordners umbenennen, dann entsteht automatisch ein neuer Ordner mit neuem Namen und der jetzige Ordner wird
            automatisch gelöscht.
            <br> <br>
            <u><b>Beispiel:</b></u><br>
            Du hast einen Ordner <code>old</code>, in dem sich die beiden Dateien <code>First.java</code> und
            <code>Second.java</code> befinden. Mit vollem Namen lauten diese Dateien <code>old/First.java</code> und
            <code>old/Second.java</code>. Wenn du die Dateien nacheinander in <code>new/First.java</code> und
            <code>new/Second.java</code>
            umbenennst, entspricht das dem Umbenennen des Ordners von <code>old</code> zu <code>new</code>.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Verstanden</button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="renameFileModal" tabindex="-1" aria-labelledby="renameFileLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Datei umbenennen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Gib den neuen Dateinamen für die Datei <u>{{ state.renameFilePath }}</u> ein. Denke an die Dateiendung
            (typischerweise <i>.java</i>)!

            <div class="input-group my-3">
              <input type="text" class="form-control" id="renameFilenameInput" :placeholder="state.renameFilePath"
                v-model="state.renameFileNewName" @keyup.enter="renameFile()">
            </div>

            <div v-if="state.newFileNameInvalid" class="alert alert-danger" role="alert">
              Dateiname ist ungültig (enthält Leerzeichen oder der Name existiert bereits)!
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
            <button type="button" class="btn btn-primary" @click.prevent="renameFile()">
              <span v-if="!state.isRenamingFile">Umbenennen</span>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>


    <div class="modal fade" id="createHomeworkModal" tabindex="-1" aria-labelledby="createHomeworkModalLabel"
      aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Hausaufgabe erstellen</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <span>⚠️<b>Wichtig:</b> Die Konfiguration eines Projektes sollte vollständig abgeschlossen sein,
              <b>bevor</b>
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
                <ul class="dropdown-menu courseDropdown" data-bs-theme="light">
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
                Bearbeitungszeit: <em v-if="homework.deadlineDate > new Date()"><b>{{ Math.floor((homework.deadlineDate
                  -
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
                <input class="hwTimeInput" :value="homework.computationTime"
                  @input="event => homework.computationTime = event.target.value" type="number" min="3" step="1"
                  placeholder="Mindestens 3, Standard 10" />
                <br>
                {{ homework.computationTime }} Sekunden
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
            <button type="button" class="btn btn-primary" @click.prevent="createHomework()"
              :disabled="Object.keys(homework.selectedCourse).length === 0 || homework.deadlineDate <= new Date() || !(homework.computationTime >= 3 && Number.isInteger(Number(homework.computationTime)))">
              <div v-if="!state.isCreatingHomework">
                Hausaufgabe erstellen
              </div>
              <div v-else class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="restartHomeworkBranchModal" tabindex="-1"
      aria-labelledby="restartHomeworkBranchModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Hausaufgabe neu beginnen?
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Möchtest du deinen bisherigen Fortschritt löschen und anschließend wieder in
            einem "sauberen" Projekt von vorne beginnen?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Abbrechen
            </button>
            <button @click.prevent="deleteHomework()" type="button" class="btn btn-primary">
              <span v-if="!state.isResettingHomework">Neu beginnen</span>
              <span v-else>
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- Navbar -->
    <nav class="navbar sticky-top navbar-expand-lg">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse d-flex" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item dropdown mx-3">
              <a class="dropdown-toggle btn btn-outline-secondary" role="button" data-bs-toggle="dropdown"
                aria-expanded="false">
                Projekt
              </a>
              <ul class="dropdown-menu" data-bs-theme="light">
                <li>
                  <a class="dropdown-item" @click.prevent="prepareAddFileModal()"><font-awesome-icon
                      icon="fa-solid fa-file-circle-plus" fixed-width />
                    Neue Datei
                  </a>
                </li>
                <li class="dropdown-divider"></li>
                <li v-if="state.isHomework && route.params.user_id != 0">
                  <a class="dropdown-item" @click.prevent="prepareDeleteHomework()">
                    <font-awesome-icon icon="fa-solid fa-trash" fixed-width /> Hausaufgabe neu beginnen
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" @click.prevent="downloadProject(route.params.project_uuid)"><font-awesome-icon
                      icon="fa-solid fa-download" fixed-width /> Projekt
                    herunterladen</a>
                </li>
              </ul>
            </li>
            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button @click.prevent="undo()" type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-rotate-left" />
              </button>
              <button @click.prevent="redo()" type="button" class="btn btn-outline-secondary">
                <font-awesome-icon icon="fa-solid fa-arrow-rotate-right" />
              </button>
            </div>

            <div class="btn-group mx-3" role="group" aria-label="Basic example">
              <button @click.prevent="saveAllBtn()" type="button" class="btn btn-green"
                :disabled="state.tabsWithChanges.length == 0" data-bs-trigger="hover" data-bs-toggle="tooltip"
                data-bs-title="Strg + s" data-bs-delay='{"show":500,"hide":0}' data-bs-placement="bottom">
                <div v-if="state.isSaving" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-floppy-disk" />
                Speichern
              </button>
              <button @click.prevent="compileBtn()" type="button" class="btn btn-yellow" data-bs-trigger="hover"
                data-bs-toggle="tooltip" data-bs-title="Strg + 1" data-bs-delay='{"show":500,"hide":0}'
                data-bs-placement="bottom">
                <div v-if="state.isCompiling" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid btn-yellow fa-gear" />
                Kompilieren
              </button>
              <button @click.prevent="executeBtn()" type="button" class="btn btn-blue" data-bs-trigger="hover"
                data-bs-toggle="tooltip" data-bs-title="Strg + 2" data-bs-delay='{"show":500,"hide":0}'
                data-bs-placement="bottom">
                <div v-if="state.isExecuting" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-circle-play" />
                Ausführen
              </button>
              <button v-if="authStore.isTeacher() || state.isHomework" @click.prevent="testBtn()" type="button"
                class="btn btn-indigo" data-bs-trigger="hover" data-bs-toggle="tooltip" data-bs-title="Strg + 3"
                data-bs-delay='{"show":500,"hide":0}' data-bs-placement="bottom">
                <div v-if="state.isTesting" class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <font-awesome-icon v-else icon="fa-solid fa-list-check" /> Testen
              </button>
            </div>
            <button :class="{ hidden: !state.isExecuting && !state.isTesting }" @click.prevent="stopContainer()"
              type="button" class="btn btn-outline-danger me-3">
              <div v-if="state.isStopping" class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <font-awesome-icon v-else icon="fa-solid fa-ban" /> Abbrechen
            </button>
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
          <ColorModeSwitch @setLight="setLight" class="ms-auto me-2" />
          <a class=" btn btn-primary" @click.prevent="checkExit()">Schließen <font-awesome-icon icon="fa-solid fa-xmark"
              size="xl" /></a>
        </div>
      </div>
    </nav>

    <div class="ide-main">
      <splitpanes class="default-theme" height="100%" horizontal :push-other-panes="false">
        <pane>
          <splitpanes :push-other-panes="false">
            <pane size="20" min-size="15" max-size="30">
              <splitpanes horizontal :push-other-panes="false">
                <pane>
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
                  <IDEFileTree :files="state.files" @openFile="openFile" @renameFile="renameFileModal"
                    @deleteFile="deleteFileModal" @renameDirectory="renameDirectoryModal"
                    @deleteDirectory="deleteDirectoryModal" />
                </pane>
                <!-- Description -->
                <pane min-size="30" size="50" max-size="70">
                  <div v-if="!state.editingDescription" class="description p-1">
                    <div class="description-content">
                      {{ state.projectDescription }}
                    </div>
                    <div v-if="route.params.user_id == 0" class="description-button bottom-0 end-0">
                      <a @click.prevent="editDescription()" class="btn btn-overlay btn-outline-secondary">
                        <div>
                          <font-awesome-icon icon="fa-pencil" />
                        </div>
                      </a>
                    </div>
                  </div>

                  <div v-else class="position-relative edit-description">
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
              <div class="editor-relative d-flex flex-column">
                <ul class="nav nav-tabs pt-2">
                  <li class="nav-item" v-for="f in state.openFiles">
                    <div class="nav-link tab" @click.prevent="openFile(f.path)" :id="'fileTab' + f.tab" :class="{
                      active: f.tab == state.activeTab,
                    }">
                      <div class="d-inline me-1" :class="{ changed: state.tabsWithChanges.includes(f.tab) }">
                        {{ f.path }}
                      </div>
                      <a v-if="f.path !== 'Schoco.java'" @click.stop="checkCloseTab(f.tab)">
                        <font-awesome-layers class="closeTabBtn">
                          <font-awesome-icon id="background" icon="fa-circle" />
                          <div style="color: var(--bs-light)">
                            <font-awesome-icon icon="fa-xmark" style="color: var(--bs-light)" transform="shrink-1" />
                          </div>
                        </font-awesome-layers>
                      </a>
                    </div>
                  </li>
                </ul>
                <v-ace-editor id="editor" value="" @init="editorInit" theme="monokai" lang="java" />
                <div class="zoom-overlay bottom-0 end-0" data-bs-theme="light">
                  <input id="zoomInput" :value="state.editorZoom" @input="event => zoom(event.target.value)" type="number"
                    :min="ZOOMMIN" :max="ZOOMMAX" step="1" />
                  <input :value="state.editorZoom" @input="event => zoom(event.target.value)" type="range"
                    class="form-range" :min="ZOOMMIN" :max="ZOOMMAX">
                </div>
              </div>
            </pane>

          </splitpanes>
        </pane>
        <pane size="20" min-size="10" max-size="50">
          <div class="bottom d-flex flex-column">
            <div class="output p-2 flex-grow-1" id="output">
              <pre ref="resultsElement">{{ results }}</pre>
            </div>
            <div class="input align-items-center d-flex flex-row">
              <label for="inputMessage" class="px-2 col-form-label">Eingabe:</label>
              <input class="rounded flex-fill" :disabled="!state.websocket_open" @keyup.enter="sendMessage()" type="text"
                id="inputMessage" v-model="state.sendMessage" placeholder="Eingabe (Entertaste zum Senden)" />
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


<style scoped lang="scss">
.hidden {
  visibility: hidden;
}

.hwTimeInput {
  background-color: white;
  color: #333
}

.courseDropdown {
  min-width: 0;
}

[data-bs-theme=light] {
  .navbar {
    background-color: #f4f4f4;
  }

  .splitpanes.default-theme .splitpanes__pane {
    background-color: #e4e4e4;
  }

  input[type="range"]::-moz-range-track {
    background-color: #ddd;
  }

  input[type="range"]::-webkit-slider-runnable-track {
    background-color: #ddd;
  }
}


[data-bs-theme=dark] {
  .navbar {
    background-color: black;
  }

  .splitpanes.default-theme .splitpanes__pane {
    background-color: inherit;
  }
}


.closeTabBtn {
  color: grey;
  transition: 0.3s;
}

.closeTabBtn:hover {
  color: red;
}

#zoomInput {
  float: right;
  width: 60px;
}

.editor-relative {
  width: 100%;
  height: 100%;
  position: relative;
}

.zoom-overlay {
  position: absolute;
  z-index: 10;
  padding: 5px;
  margin-right: 20px;
  width: 200px;
}

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
  font-family: monospace;
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
  font-family: monospace;
  white-space: pre-line;
  display: block;
  height: 100%;
  position: relative;
}

.description-content {
  position: absolute;
  height: 100%;
  width: 100%;
  overflow-y: auto;
}

.description-button {
  position: absolute;
}

.bottom {
  width: 100%;
  height: 100%;
  /* background-color: #383838; */
}

.input {
  border-top: 1px solid #ccc;
}

.output {
  width: 100%;
  /* height: 100%; */
  /* background-color: #383838; */
  font-family: "Courier New", Courier, monospace;
  overflow-y: auto;
}

.changed {
  font-style: italic;
}

.changed::after {
  content: "*";
}


[data-bs-theme=dark] {
  .tab:not(.active) {
    border-left: 1px solid #6a6a6a;
    border-top: 1px solid #6a6a6a;
    border-right: 1px solid #6a6a6a;
    background-color: #6a6a6a;
    color: lightgray;
  }

  .tab.active {
    border-left: 2px solid $primary;
    border-top: 2px solid $primary;
    border-right: 2px solid $primary;
  }
}

[data-bs-theme=light] {
  .tab:not(.active) {
    border-left: 1px solid #ccc;
    border-top: 1px solid #ccc;
    border-right: 1px solid #ccc;
    background-color: #eee;
    color: gray;
  }

  .tab.active {
    border-left: 2px solid $primary;
    border-top: 2px solid $primary;
    border-right: 2px solid $primary;
  }
}

.tab:hover {
  cursor: pointer;
}

.active {
  font-weight: bold;
}

#editor {
  position: relative;
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
