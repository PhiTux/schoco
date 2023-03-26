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
})

onBeforeMount(() => {
    CodeService.getHomeworkInfo(route.params.id).then(
        response => {
            console.log(response.data)
            state.name = response.data.name;
            state.course_name = response.data.course_name;
            state.course_color = response.data.course_color;
            state.course_font_dark = response.data.course_font_dark;
        },
        error => {
            console.log(error.response)
        }
    )
})

</script>

<template>
    <div class="container">
        <h2>
            <CourseBadge :name="state.course_name" :color="state.course_color" :font-dark="state.course_font_dark">
            </CourseBadge> {{ state.name }}
        </h2>

        <table class="table table-dark table-striped table-hover align-middle">
            <thead>
                <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Username</th>
                    <th scope="col"></th>
                    <th scope="col">(Ergebnis)</th>
                    <th scope="col">(# Kompilierungen)</th>
                    <th scope="col">(# Ausführungen)</th>
                    <th scope="col">(# Tests)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.container {
    margin-top: 1em;
}
</style>