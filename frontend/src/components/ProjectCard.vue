<script setup>
import CourseBadge from "./CourseBadge.vue"

defineProps({
    name: String,
    description: String,
    deadline: String,
    uuid: String,
    id: String,
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

</script>

<template>
    <div class="card text-bg-dark m-2" :class="{ homeworkBorder: isHomework, old_homework: isOld }">
        <div v-if="isHomework" class="card-header">HA | Abgabe bis <span class="deadline">{{ new
            Date(deadline).toLocaleString("default", {
                weekday: "long", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"
            }) }}</span></div>
        <div class="card-body">

            <h5 class="card-title">
                <CourseBadge v-if="isTeacher && isHomework" :color="courseColor" :font-dark="courseFontDark"
                    :name="courseName"></CourseBadge>{{ name }}
            </h5>
            <p class="card-text">
                {{ description }}
            </p>
            <!-- :href="'#/startHomework/' + id" -->
            <a v-if="!isTeacher && isHomework && !isEditing" @click.prevent="$emit('startHomework', id)" 
                class="btn btn-primary">🌟Hausaufgabe
                beginnen</a>
            <a v-else-if="!isTeacher && isHomework && isEditing" :href="'#/ide/' + uuid" class="btn btn-primary">Hausaufgabe
                bearbeiten</a>
            <a v-else-if="isTeacher && isHomework" :href="'#/homework/' + id" class="btn btn-primary">Details zeigen</a>
            <a v-else-if="!isHomework" :href="'#/ide/' + uuid" class="btn btn-primary">Projekt öffnen</a>
        </div>
    </div>
</template>

<style scoped>
.old_homework {
    border-color: darkorange !important;
    color: lightgray !important;
}

.deadline {
    text-decoration: underline;
    text-decoration-color: yellow;
}

.homeworkBorder {
    border-color: yellow;
}

.card {
    width: 48%;
    transition: ease 0.3s;
}

.card:hover {
    box-shadow: 0 0 10px 3px #555;
}
</style>