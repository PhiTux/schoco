<script setup>
import { onBeforeMount, ref } from 'vue';

let mode = ref('auto');

onBeforeMount(() => {
    if (localStorage.getItem('theme') === 'dark') {
        setDark();
        mode.value = 'dark';
    } else if (localStorage.getItem('theme') === 'light') {
        setLight();
        mode.value = 'light';
    } else {
        auto();
        mode.value = 'auto';
    }
})

function setLight() {
    document.documentElement.setAttribute('data-bs-theme', 'light')
}

function setDark() {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
}

function manualLight() {
    setLight()
    localStorage.setItem('theme', 'light');
    mode.value = 'light';
}

function manualDark() {
    setDark()
    localStorage.setItem('theme', 'dark');
    mode.value = 'dark';
}

function manualAuto() {
    localStorage.removeItem('theme');
    auto();
    mode.value = 'auto';
}

function auto() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setDark();
    } else {
        setLight();
    }
}

</script>

<template>
    <div class="dropdown">
        <button class="dropdown-toggle btn btn-outline-secondary" href="#" role="button" data-bs-toggle="dropdown"
            aria-expanded="false">
            <font-awesome-icon icon="fa-solid fa-sun" fixed-width />/<font-awesome-icon icon="fa-solid fa-moon"
                fixed-width />
        </button>
        <ul class="dropdown-menu dropdown-menu-end" data-bs-theme="light">
            <li>
                <a class="dropdown-item" :class="{ active: mode === 'light' }" @click.prevent="manualLight()">
                    <font-awesome-icon icon="fa-solid fa-sun" fixed-width /> Light
                </a>
            </li>
            <li>
                <a class="dropdown-item" :class="{ active: mode === 'dark' }" @click.prevent="manualDark()">
                    <font-awesome-icon icon="fa-solid fa-moon" fixed-width /> Dark
                </a>
            </li>
            <li>
                <a class="dropdown-item" :class="{ active: mode === 'auto' }" @click.prevent="manualAuto()">
                    <font-awesome-icon icon="fa-solid fa-circle-half-stroke" fixed-width /> Auto
                </a>
            </li>
        </ul>
    </div>
</template>

<style scoped>
a {
    cursor: pointer;
}

.dropdown-menu {
    min-width: 0;
}
</style>