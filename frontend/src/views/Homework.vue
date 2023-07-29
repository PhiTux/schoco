<script setup>
import { onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";
import CodeService from "../services/code.service.js";
import CourseBadge from "../components/CourseBadge.vue";
import { Modal, Popover } from "bootstrap";

const route = useRoute()

let state = reactive({
    name: "",
    course_name: "",
    course_color: "",
    course_font_dark: true,
    pupils: [],
    showDetails: false,
    uuid: "",
})

let homework = reactive({
    deadlineDate: new Date(),
    computationTime: 10,
})

onBeforeMount(() => {
    CodeService.getHomeworkInfo(route.params.id).then(
        response => {
            state.name = response.data.name;
            state.course_name = response.data.course_name;
            state.course_color = response.data.course_color;
            state.course_font_dark = response.data.course_font_dark;
            state.pupils = response.data.pupils_results;
            state.uuid = response.data.uuid;

            homework.deadlineDate = new Date(response.data.deadline)
            homework.computationTime = response.data.computation_time

            document.title = state.name
        },
        error => {
            console.log(error.response)
            document.title = "Unbekannte Hausaufgabe"
        }
    )
})

function calc_result(input_string) {
    let input = JSON.parse(input_string)
    return Math.round(input.passed_tests / (input.passed_tests + input.failed_tests) * 100 * 10) / 10
}

function calc_result_color(input_string) {
    let result = calc_result(input_string)
    if (result <= 30)
        return 1
    if (result <= 90)
        return 2
    return 3
}

function prepareEditHomeworkModal() {
    //open Modal
    let myModal = new Modal(document.getElementById('editHomeworkModal'))
    myModal.show()

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new Popover(popoverTriggerEl, { trigger: 'focus', html: true }))
}

</script>

<template>
    <div class="modal fade" id="editHomeworkModal" tabindex="-1" aria-labelledby="editHomeworkModalLabel"
        aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="exampleModalLabel">Hausaufgabe bearbeiten</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 row">
                        <label for="coursename" class="col-sm-4 col-form-label">
                            <font-awesome-icon icon="fa-square-check" style="color: var(--bs-success)" />
                        </label>
                        <div class="col-sm-8 d-flex align-items-center">
                            <CourseBadge :color="state.course_color" :font-dark="state.course_font_dark"
                                :name="state.course_name" />
                            <a class="btn-round btn" data-bs-trigger="focus" tabindex="0" data-bs-toggle="popover"
                                title="Kurs ändern"
                                data-bs-content="Du kannst bei einer bereits erstellten Hausaufgabe den Kurs <b>nicht mehr ändern</b>!<br/>Du kannst die Hausaufgabe nur in <a href='/'>Home</a> löschen und anschließend für einen anderen Kurs neu erstellen.">
                                <font-awesome-icon icon="fa-circle-exclamation" size="lg"
                                    style="color: var(--bs-primary)" />
                            </a>
                        </div>
                    </div>
                    <div class="mb-3 row">
                        <label for="deadline" class="col-sm-4 col-form-label">
                            <font-awesome-icon v-if="homework.deadlineDate > new Date()" icon="fa-square-check"
                                style="color: var(--bs-success)" />
                            <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" />
                            Abgabefrist:</label>
                        <div class="col-sm-8">
                            <!-- Sadly can't use the option :format-locale="de" because then I can't manually edit the input-field for some reason... -->
                            <VueDatePicker v-model="homework.deadlineDate" placeholder="Start Typing ..." text-input
                                auto-apply :min-date="new Date()" prevent-min-max-navigation locale="de"
                                format="E dd.MM.yyyy, HH:mm" />
                            UTC: <em>{{ homework.deadlineDate.toISOString() }}</em><br>
                            Bearbeitungszeit: <em v-if="homework.deadlineDate > new Date()"><b>{{
                                Math.floor((homework.deadlineDate
                                    -
                                    new Date()) / (1000 * 3600 * 24)) }} Tage,
                                    {{ Math.floor((homework.deadlineDate - new Date()) / (1000 * 3600) % 24) }}
                                    Stunden</b></em>
                        </div>
                    </div>
                    <div class="mb-3 row">
                        <label for="deadline" class="col-sm-4 col-form-label">
                            <font-awesome-icon
                                v-if="homework.computationTime >= 3 && Number.isInteger(Number(homework.computationTime))"
                                icon="fa-square-check" style="color: var(--bs-success)" />
                            <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" /> Rechenzeit:
                            <a class="btn-round btn" data-bs-trigger="focus" tabindex="0" data-bs-toggle="popover"
                                title="Rechenzeit"
                                data-bs-content="Lege fest, wie viele <b>Sekunden</b> Rechenzeit (bzw. genauer: Laufzeit) auf dem Server pro Aktion zur Verfügung stehen. Als Aktion gilt:<ul><li>Kompilieren</li><li>Ausführen</li><li>Testen</li></ul>Der Standardwert beträgt 10 Sekunden, welchen Schüler/innen in eigenen Projekten auch <b>nicht</b> verändern können, da der Server mit endlos laufenden Programmen lahm gelegt werden könnte. Unter Umständen kann es aber sinnvoll sein, bei Hausaufgaben die Laufzeit zu verlängern, z. B. wenn ein Programm auf Benutzereingaben warten muss, welche auch ihre Zeit brauchen.">
                                <font-awesome-icon icon="fa-circle-question" size="lg" style="color: var(--bs-primary)" />
                            </a>
                        </label>
                        <div class="col-sm-8">
                            <input class="hwTimeInput" :value="homework.computationTime"
                                @input="event => homework.computationTime = event.target.value" type="number" min="3"
                                step="1" placeholder="Mindestens 3, Standard 10" data-bs-theme="light" />
                            <br>
                            {{ homework.computationTime }} Sekunden
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
                    <button type="button" class="btn btn-primary" @click.prevent="updateSettings()"
                        :disabled="homework.deadlineDate <= new Date() || !(homework.computationTime >= 3 && Number.isInteger(Number(homework.computationTime)))">
                        <div v-if="!state.isCreatingHomework">
                            Speichern
                        </div>
                        <div v-else class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <h2>
            <CourseBadge :name="state.course_name" :color="state.course_color" :font-dark="state.course_font_dark">
            </CourseBadge> {{ state.name }}
        </h2>

        <div class="d-flex mb-3">
            <div class="p-2 ">
                <div class="my-3 form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="showDetails"
                        v-model="state.showDetails">
                    <label class="form-check-label disable-select" for="showDetails">Zeige Ergebnisse</label>
                </div>
            </div>
            <div class="ms-auto p-2">
                <a class="btn btn-secondary" @click="prepareEditHomeworkModal()">
                    <font-awesome-icon icon="fa-solid fa-gear" fixed-width /> Einstellungen
                </a>
            </div>
            <div class="p-2">
                <a class="btn btn-secondary" :href="'#/ide/' + state.uuid + '/0'">
                    <font-awesome-icon icon="fa-solid fa-code" fixed-width /> Vorlage bearbeiten
                </a>
            </div>
        </div>


        <table class="table table-striped table-hover align-middle">
            <thead>
                <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Username</th>
                    <th scope="col"></th>
                    <th scope="col">Ergebnis</th>
                    <th scope="col"># Kompilierungen</th>
                    <th scope="col"># Ausführungen</th>
                    <th scope="col"># Tests</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="p in state.pupils">
                    <td>{{ p.name }}</td>
                    <td>{{ p.username }}</td>
                    <td><a class="btn btn-primary" v-if="p.uuid !== ''"
                            :href="'#/ide/' + p.uuid + '/' + p.branch">Öffnen</a></td>
                    <td><span v-if="state.showDetails && p.result"
                            :class="{ resultRed: calc_result_color(p.result) == 1, resultYellow: calc_result_color(p.result) == 2, resultGreen: calc_result_color(p.result) == 3 }">{{
                                calc_result(p.result) }} %</span><span v-else-if="state.showDetails">0
                            %</span></td>
                    <td><span v-if="state.showDetails">{{ p.compilations }}</span></td>
                    <td><span v-if="state.showDetails">{{ p.runs }}</span></td>
                    <td><span v-if="state.showDetails">{{ p.tests }}</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.hwTimeInput {
    background-color: white;
    color: #333
}

.resultGreen {
    color: green;
}

.resultYellow {
    color: yellow;
}

.resultRed {
    color: red;
}

.container {
    margin-top: 1em;
}

.disable-select {
    user-select: none;
}
</style>