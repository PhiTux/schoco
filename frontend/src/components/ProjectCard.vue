<script setup>
defineProps({
    name: String,
    description: String,
    deadline: String,
    uuid: String,
    id: String,
    isTeacher: Boolean,
    isHomework: Boolean,
    isNew: Boolean,
    pupilsWorking: Number,
    averageSolution: Number,
    Course: String,
    lastEdited: String,
    evaluation: Number
});

</script>

<template>
    <div class="card text-bg-dark m-2" :class="{ homeworkBorder: isHomework }">
        <div v-if="isHomework" class="card-header">HA | Abgabe bis <span class="deadline">{{ new
            Date(deadline).toLocaleString("default", {
                weekday: "long", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"
            }) }}</span></div>
        <div class="card-body">
            <h5 class="card-title">{{ name }}</h5>
            <p class="card-text">
                {{ description }}
            </p>
            <a v-if="isNew && !isTeacher" :href="'#/startHomework/' + uuid" class="btn btn-primary">🌟Hausaufgabe
                beginnen</a>
            <a v-if="isTeacher" :href="'#/openHomework/' + id" class="btn btn-primary">Details zeigen</a>
            <a v-else :href="'#/ide/' + uuid" class="btn btn-primary">Projekt öffnen</a>
        </div>
    </div>
</template>

<style scoped>
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