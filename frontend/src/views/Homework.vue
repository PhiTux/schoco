<script setup>
import { onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";
import CodeService from "../services/code.service.js";
import CourseBadge from "../components/CourseBadge.vue";
import { Modal, Popover, Toast } from "bootstrap";
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useI18n } from 'vue-i18n'

const i18n = useI18n()

const route = useRoute()

let state = reactive({
    name: "",
    course_name: "",
    course_color: "",
    course_font_dark: true,
    pupils: [],
    showDetails: false,
    uuid: "",
    isUpdatingHomework: false,
})

let homework = reactive({
    deadlineDate: new Date(),
    computationTime: 10,
})

let newSettings = reactive({
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
            document.title = i18n.t("unknown_assignment")
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
    newSettings.deadlineDate = homework.deadlineDate
    newSettings.computationTime = homework.computationTime

    //open Modal
    let myModal = new Modal(document.getElementById('editHomeworkModal'))
    myModal.show()

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new Popover(popoverTriggerEl, { trigger: 'focus', html: true }))
}

function updateSettings() {
    if (state.isUpdatingHomework)
        return
    state.isUpdatingHomework = true

    CodeService.updateHomeworkSettings(route.params.id, newSettings.deadlineDate, newSettings.computationTime).then(
        response => {
            state.isUpdatingHomework = false

            if (response.data.success) {
                homework.deadlineDate = newSettings.deadlineDate
                homework.computationTime = newSettings.computationTime

                let myModal = Modal.getInstance(document.getElementById('editHomeworkModal'))
                myModal.hide()

                let toast = new Toast(document.getElementById('toastUpdateSettingsSuccess'))
                toast.show()
            } else {
                let toast = new Toast(document.getElementById('toastUpdateSettingsError'))
                toast.show()
            }
        },
        error => {
            console.log(error.response)
            state.isUpdatingHomework = false

            let toast = new Modal(document.getElementById('toastUpdateSettingsError'))
            toast.show()
        }
    )
}

</script>

<template>
    <div>
        <div class="toast-container position-fixed bottom-0 end-0 p-3">
            <div class="toast align-items-center text-bg-danger border-0" id="toastUpdateSettingsError" role="alert"
                aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        {{ $t("error_on_changing_settings") }}
                    </div>
                </div>
            </div>

            <div class="toast align-items-center text-bg-success border-0" id="toastUpdateSettingsSuccess" role="alert"
                aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        {{ $t("settings_updated") }}
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="editHomeworkModal" tabindex="-1" aria-labelledby="editHomeworkModalLabel"
            aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5" id="exampleModalLabel">{{ $t("edit_settings") }}</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3 row">
                            <label for="coursename" class="col-sm-4 col-form-label">
                                <font-awesome-icon icon="fa-square-check" style="color: var(--bs-success)" />
                                {{ $t("course") }}:
                            </label>
                            <div class="col-sm-8 d-flex align-items-center">
                                <CourseBadge :color="state.course_color" :font-dark="state.course_font_dark"
                                    :name="state.course_name" />
                                <a class="btn-round btn" data-bs-trigger="focus" tabindex="0" data-bs-toggle="popover"
                                    title="Kurs ändern" :data-bs-content="i18n.t('cant_change_course_of_assignment')">
                                    <font-awesome-icon icon="fa-circle-exclamation" size="lg"
                                        style="color: var(--bs-primary)" />
                                </a>
                            </div>
                        </div>
                        <div class="mb-3 row">
                            <label for="deadline" class="col-sm-4 col-form-label">
                                <font-awesome-icon v-if="newSettings.deadlineDate > new Date()" icon="fa-square-check"
                                    style="color: var(--bs-success)" />
                                <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" />
                                {{ $t("deadline") }}:
                            </label>
                            <div class="col-sm-8">
                                <!-- Sadly can't use the option :format-locale="de" because then I can't manually edit the input-field for some reason... -->
                                <VueDatePicker v-model="newSettings.deadlineDate" placeholder="Start Typing ..." text-input
                                    auto-apply :min-date="new Date()" prevent-min-max-navigation locale="de"
                                    :format="$t('long_date_format')" />
                                {{ $t("UTC") }}: <em>{{ newSettings.deadlineDate.toISOString() }}</em><br>
                                {{ $t("editing_time") }}: <em v-if="newSettings.deadlineDate > new Date()"><b>{{
                                    Math.floor((newSettings.deadlineDate
                                        -
                                        new Date()) / (1000 * 3600 * 24)) }} {{ $t("days") }},
                                        {{ Math.floor((newSettings.deadlineDate - new Date()) / (1000 * 3600) % 24) }}
                                        {{ $t("hours") }}</b></em>
                            </div>
                        </div>
                        <div class="mb-3 row">
                            <label for="deadline" class="col-sm-4 col-form-label">
                                <font-awesome-icon
                                    v-if="newSettings.computationTime >= 3 && Number.isInteger(Number(newSettings.computationTime))"
                                    icon="fa-square-check" style="color: var(--bs-success)" />
                                <font-awesome-icon v-else icon="fa-square" style="color: var(--bs-secondary)" />
                                {{ $t("computation_time") }}:
                                <a class="btn-round btn" tabindex="0" @click.prevent="openComputationTimePopover()"
                                    data-bs-toggle="popover" title="Rechenzeit" data-bs-trigger="focus"
                                    :data-bs-content="$t('computation_time_description')">
                                    <font-awesome-icon icon="fa-circle-question" size="lg"
                                        style="color: var(--bs-primary)" />
                                </a>

                            </label>
                            <div class="col-sm-8">
                                <input class="hwTimeInput" :value="newSettings.computationTime"
                                    @input="event => newSettings.computationTime = event.target.value" type="number" min="3"
                                    step="1" :placeholder="$t('at_least_3_default_10')" data-bs-theme="light" />
                                <br>
                                {{ newSettings.computationTime }} {{ $t("seconds") }}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{{ $t("abort") }}</button>
                        <button type="button" class="btn btn-primary" @click.prevent="updateSettings()"
                            :disabled="newSettings.deadlineDate <= new Date() || !(newSettings.computationTime >= 3 && Number.isInteger(Number(newSettings.computationTime)))">
                            <div v-if="!state.isUpdatingHomework">
                                {{ $t("save") }}
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
                        <label class="form-check-label disable-select" for="showDetails">{{ $t("show_results") }}</label>
                    </div>
                </div>
                <div class="ms-auto p-2">
                    <a class="btn btn-secondary" @click="prepareEditHomeworkModal()">
                        <font-awesome-icon icon="fa-solid fa-gear" fixed-width /> {{ $t("settings") }}
                    </a>
                </div>
                <div class="p-2">
                    <a class="btn btn-secondary" :href="'#/ide/' + state.uuid + '/0'">
                        <font-awesome-icon icon="fa-solid fa-code" fixed-width /> {{ $t("edit_template") }}
                    </a>
                </div>
            </div>


            <table class="table table-striped table-hover align-middle">
                <thead>
                    <tr>
                        <th scope="col">{{ $t("name") }}</th>
                        <th scope="col">{{ $t("username") }}</th>
                        <th scope="col"></th>
                        <th scope="col">{{ $t("result") }}</th>
                        <th scope="col">{{ $t("number_of_compilations") }}</th>
                        <th scope="col">{{ $t("number_of_runs") }}</th>
                        <th scope="col">{{ $t("number_of_tests") }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for=" p  in  state.pupils ">
                        <td>{{ p.name }}</td>
                        <td>{{ p.username }}</td>
                        <td><a class="btn btn-primary" v-if="p.uuid !== ''"
                                :href="'#/ide/' + p.uuid + '/' + p.branch">{{ $t("open") }}</a></td>
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