<script setup>
defineProps({
    name: String,
    description: String,
    deadline: String,
    uuid: String,
    isTeacher: Boolean,
    isHomework: Boolean,
    pupilsWorking: Number,
    averageSolution: Number,
    Course: String,
});
</script>

<template>
    <div class="card text-bg-dark m-2">
        <div class="card-header">HA bis ... / eigenes Projekt</div>
        <div class="card-body">
            <h5 class="card-title">{{ name }}</h5>
            <p class="card-text">
                {{ description }}
            </p>
            <a :href="'#/ide/' + uuid" class="btn btn-primary">Projekt öffnen</a>
        </div>
    </div>
</template>

<style scoped>
.card {
    width: 48%;
    transition: ease 0.3s;
}

.card:hover {
    box-shadow: 0 0 10px 3px #555;
}
</style>