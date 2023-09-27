<script setup>
import { onMounted, reactive } from "vue";
import CourseBadge from "./CourseBadge.vue"
import TextClamp from "vue3-text-clamp";

let state = reactive({
    showToggle: false
})

const props = defineProps({
    name: String,
    description: String,
    deadline: String,
    uuid: String,
    branch: Number,
    id: Number,
    isTeacher: Boolean,
    isHomework: Boolean,
    isEditing: Boolean,
    isOld: Boolean,
    pupilsWorking: Number,
    averageSolution: Number,
    courseColor: String,
    courseFontDark: Boolean,
    courseName: String,
    lastEdited: String,
    evaluation: Number,
    solution_uuid: String,
    solution_name: String,
    solution_id: Number,
    solution_start_showing: String
});

onMounted(() => {
    if (props.isHomework) {
        let e = document.getElementById("description-" + props.id)
        if (e.innerText != props.description) {
            state.showToggle = true
        }
    } else {
        let e = document.getElementById("description-" + props.uuid)
        if (e.innerText != props.description) {
            state.showToggle = true
        }
    }
})

</script>

<template>
    <div class="card m-2" :class="{ homeworkBorder: isHomework, old_homework: isOld }">
        <div v-if="isHomework" class="card-header"> 💡 |
            {{ $t("submit_until") }}
            <span class="deadline">{{ new
                Date(deadline).toLocaleString("default", {
                    weekday: "long", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"
                }) }}</span>
        </div>
        <div class="card-body">

            <div class="d-flex align-items-center">
                <h5 class="card-title d-inline-flex">
                    <CourseBadge v-if="isTeacher && isHomework" :color="courseColor" :font-dark="courseFontDark"
                        :name="courseName"></CourseBadge>{{ name }}
                </h5>
                <!-- Menu -->
                <a class="menuButton ms-auto" data-bs-toggle="dropdown"><font-awesome-icon icon="fa-bars" fixed-width /></a>
                <ul class="dropdown-menu" data-bs-theme="light">
                    <li v-if="!isHomework"><a class="dropdown-item"
                            @click="$emit('renameProject', uuid, name)"><font-awesome-icon icon="fa-solid fa-pencil"
                                fixed-width /> {{ $t("rename") }}</a></li>
                    <li v-if="isHomework && isTeacher"><a class="dropdown-item"
                            @click="$emit('renameHomework', id, name)"><font-awesome-icon icon="fa-solid fa-pencil"
                                fixed-width /> {{ $t("rename") }}</a></li>
                    <li v-if="!isHomework"><a class="dropdown-item"
                            @click="$emit('duplicateProject', uuid)"><font-awesome-icon icon="fa-solid fa-copy"
                                fixed-width /> {{ $t("duplicate") }}</a></li>
                    <li v-if="!isHomework"><a class="dropdown-item"
                            @click="$emit('downloadProject', uuid)"><font-awesome-icon icon="fa-solid fa-download"
                                fixed-width /> {{ $t("download") }}</a></li>
                    <li v-if="isHomework && isTeacher"><a class="dropdown-item"
                            @click.prevent="$emit('deleteHomework', id, name)"><font-awesome-icon icon="fa-solid fa-trash"
                                fixed-width /> {{ $t("delete") }}</a></li>
                    <li v-else-if="isHomework && !isTeacher"><a class="dropdown-item"
                            @click.prevent="$emit('deleteHomeworkBranch', uuid, branch, name)"><font-awesome-icon
                                icon="fa-solid fa-trash" fixed-width /> {{ $t("delete") }}</a></li>
                    <li v-else><a class="dropdown-item"
                            @click.prevent="$emit('deleteProject', uuid, branch, name)"><font-awesome-icon
                                icon="fa-solid fa-trash" fixed-width /> {{ $t("delete") }}</a></li>
                </ul>
            </div>

            <text-clamp :id="props.isHomework ? 'description-' + props.id : 'description-' + props.uuid" class="text-clamp"
                :text="description" :max-lines="2">
                <template #after="{ toggle, clamped }">
                    <a v-if="state.showToggle" class="description-toggle" @click="toggle">
                        {{ clamped == true ? $t("more") : $t("less") }}
                    </a>
                </template>
            </text-clamp>

            <div class="mt-2 d-flex align-items-center flex-wrap">
                <div class="">
                    <a v-if="!isTeacher && isHomework && !isEditing" @click.prevent="$emit('startHomework', id)"
                        class="btn btn-primary">🌟{{ $t("begin_assignment") }}</a>
                    <router-link v-else-if="!isTeacher && isHomework && isEditing" :to="'/ide/' + uuid + '/' + branch"
                        class="btn btn-primary">{{ $t("edit_assignment") }}</router-link>
                    <router-link v-else-if="isTeacher && isHomework" :to="'/homework/' + id" class="btn btn-primary">{{
                        $t("show_details") }}</router-link>
                    <router-link v-else-if="!isHomework" :to="'/ide/' + uuid + '/' + 0" class="btn btn-primary">{{
                        $t("open_project") }}</router-link>
                </div>
                <div v-if="isTeacher && isHomework" class="ms-auto input-group solution" style="width: auto;">
                    <div class="p-1 border border-success input-group-text" v-if="isHomework && solution_id != 0">
                        {{ solution_name }}<br>
                        {{ new Date(solution_start_showing).toLocaleString("default", {
                            weekday: "short", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute:
                                "2-digit"
                        }) }}
                    </div>

                    <a @click.prevent="$emit('addSolution', id)" class="btn btn-outline-success"
                        :class="{ borderDashed: solution_id == 0 }">
                        <span v-if="solution_id == 0">{{ $t("add_solution") }}</span>
                        <span v-else v-html="$t('change_solution')"></span>
                    </a>
                    <a v-if="solution_id != 0" @click.prevent="$emit('deleteSolution', id)"
                        class="btn btn-outline-danger d-flex align-items-center">
                        <font-awesome-icon icon="fa-solid fa-trash" fixed-width />
                    </a>
                </div>
                <div v-else-if="!isTeacher && isHomework && solution_uuid !== ''" class="ms-auto">
                    <router-link :to="'/ide/' + solution_uuid + '/0'" class="btn btn-success">{{ $t("open_solution")
                    }}</router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
@media (max-width: 1199px) {
    .solution {
        width: 100% !important;
        justify-content: center !important;
        margin-top: 10px;
    }
}

@media (max-width: 991px) {
    .card {
        width: 100% !important;
    }
}

.think_img {
    height: 1em;
}

.borderDashed {
    border-style: dashed;
}

.text-clamp {
    white-space: pre-line;
}


.description-toggle {
    margin-left: 0.5rem;
    color: $primary;
    cursor: pointer;
}


.dropdown-item {
    cursor: pointer;
}

.card:hover .menuButton {
    color: $primary;
}

.card .menuButton {
    cursor: pointer;
    color: rgb(54, 54, 54);
    transition: ease 0.3s;
}

.old_homework {
    border-color: darkorange !important;
    color: darkgray !important;
    box-shadow: none !important;
}

.deadline {
    text-decoration: underline;
    text-decoration-color: yellow;
}

.homeworkBorder {
    border-color: orange;
    border-width: 1px;
    box-shadow: 0 0 3px 2px yellow;
}


.card {
    /* min-width: 536px; */
    width: 48%;
    transition: all 0.3s ease;

    [data-bs-theme=light] & {
        background-color: #fafafa;
    }

    [data-bs-theme=dark] & {
        background-color: #292e33;
    }
}

/* .card-body {
    
} */

.card:hover {
    box-shadow: 0 0 10px 3px #555 !important;
}
</style>