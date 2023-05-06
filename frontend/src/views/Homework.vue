<script setup>
import { onBeforeMount, reactive } from "vue";
import { useRoute } from "vue-router";
import CodeService from "../services/code.service.js";
import CourseBadge from "../components/CourseBadge.vue";

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

onBeforeMount(() => {
    CodeService.getHomeworkInfo(route.params.id).then(
        response => {
            state.name = response.data.name;
            state.course_name = response.data.course_name;
            state.course_color = response.data.course_color;
            state.course_font_dark = response.data.course_font_dark;
            state.pupils = response.data.pupils_results;
            state.uuid = response.data.uuid;
        },
        error => {
            console.log(error.response)
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

</script>

<template>
    <div class="container">
        <h2>
            <CourseBadge :name="state.course_name" :color="state.course_color" :font-dark="state.course_font_dark">
            </CourseBadge> {{ state.name }}
        </h2>

        <div class="d-flex mb-3">
            <div class="p-2">
                <div class="my-3 form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="showDetails"
                        v-model="state.showDetails">
                    <label class="form-check-label disable-select" for="showDetails">Zeige Ergebnisse</label>
                </div>
            </div>
            <div class="ms-auto p-2"><a class="btn btn-secondary" :href="'#/ide/' + state.uuid + '/0'">Vorlage
                    bearbeiten</a>
            </div>
        </div>


        <table class="table table-dark table-striped table-hover align-middle">
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