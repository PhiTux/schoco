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
    evaluation: Number
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
        <div v-if="isHomework" class="card-header">HA | Abgabe bis <span class="deadline">{{ new
            Date(deadline).toLocaleString("default", {
                weekday: "long", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"
            }) }}</span></div>
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
                                fixed-width /> Umbenennen</a></li>
                    <li v-if="isHomework && isTeacher"><a class="dropdown-item"
                            @click="$emit('renameHomework', id, name)"><font-awesome-icon icon="fa-solid fa-pencil"
                                fixed-width /> Umbenennen</a></li>
                    <li v-if="!isHomework"><a class="dropdown-item"
                            @click="$emit('duplicateProject', uuid)"><font-awesome-icon icon="fa-solid fa-copy"
                                fixed-width /> Duplizieren</a></li>
                    <li v-if="!isHomework"><a class="dropdown-item"
                            @click="$emit('downloadProject', uuid)"><font-awesome-icon icon="fa-solid fa-download"
                                fixed-width /> Download</a></li>
                    <li v-if="isHomework && isTeacher"><a class="dropdown-item"
                            @click.prevent="$emit('deleteHomework', id, name)"><font-awesome-icon icon="fa-solid fa-trash"
                                fixed-width /> Löschen</a></li>
                    <li v-else-if="isHomework && !isTeacher"><a class="dropdown-item"
                            @click.prevent="$emit('deleteHomeworkBranch', uuid, branch, name)"><font-awesome-icon
                                icon="fa-solid fa-trash" fixed-width /> Löschen</a></li>
                    <li v-else><a class="dropdown-item"
                            @click.prevent="$emit('deleteProject', uuid, branch, name)"><font-awesome-icon
                                icon="fa-solid fa-trash" fixed-width /> Löschen</a></li>
                </ul>
            </div>

            <text-clamp :id="props.isHomework ? 'description-' + props.id : 'description-' + props.uuid" class="text-clamp"
                :text="description" :max-lines="2">
                <template #after="{ toggle, clamped }">
                    <a v-if="state.showToggle" class="description-toggle" @click="toggle">
                        {{ clamped == true ? "mehr" : "weniger" }}
                    </a>
                </template>
            </text-clamp>

            <div class="mt-2 d-flex align-items-center">
                <a v-if="!isTeacher && isHomework && !isEditing" @click.prevent="$emit('startHomework', id)"
                    class="btn btn-primary">🌟Hausaufgabe
                    beginnen</a>
                <a v-else-if="!isTeacher && isHomework && isEditing" :href="'#/ide/' + uuid + '/' + branch"
                    class="btn btn-primary">Hausaufgabe
                    bearbeiten</a>
                <a v-else-if="isTeacher && isHomework" :href="'#/homework/' + id" class="btn btn-primary">Details zeigen</a>
                <a v-else-if="!isHomework" :href="'#/ide/' + uuid + '/' + 0" class="btn btn-primary">Projekt öffnen</a>
            </div>
        </div>
    </div>
</template>

<style scoped lang="scss">
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