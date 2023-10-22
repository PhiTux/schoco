<script setup>
import { onMounted, watch } from "vue";
import { Tooltip } from "bootstrap";
import { useRoute } from 'vue-router';

const route = useRoute();


const props = defineProps({
    path: String,
    name: String,
    value: Object,
    renameAllowed: Boolean,
    deleteAllowed: Boolean,
    entryPoint: String,
})

const emit = defineEmits(['openFile', 'renameFile', 'deleteFile', 'renameDirectory', 'deleteDirectory', 'setEntryPoint'])

function openFile(path) {
    emit('openFile', path)
}

function renameFile(path) {
    emit('renameFile', path)
}

function deleteFile(path) {
    emit('deleteFile', path)
}

function renameDirectory() {
    emit('renameDirectory')
}

function deleteDirectory() {
    emit('deleteDirectory')
}

function setEntryPoint(path) {
    emit('setEntryPoint', path)
}

function updateTooltip() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl, { trigger: 'hover' }))
}

onMounted(() => {
    updateTooltip();
})

watch(() => props.entryPoint, () => {
    setTimeout(() => {
        updateTooltip();
    }, 250);
})

</script>

<template>
    <li class="my-2">
        <font-awesome-icon v-if="Object.keys(props.value).length !== 0" icon="fa-solid fa-folder-open" class="mx-1 treeItem"
            fixed-width />
        <font-awesome-icon v-else icon="fa-solid fa-file" class="mx-1 treeItem" fixed-width />
        <div class="btn-group">
            <a v-if="Object.keys(props.value).length === 0" @click="$emit('openFile', props.path)">
                <div class="d-flex name px-1"><font-awesome-icon v-if="props.entryPoint === props.path"
                        data-bs-toggle="tooltip" data-bs-placement="top" :data-bs-title="$t('tooltip_entry_point')"
                        icon="fa-solid fa-house" class="mx-1 treeItem my-auto" fixed-width /> {{ props.name }}</div>
            </a>
            <a v-else>
                <div class="name px-1">{{ props.name }}</div>
            </a>
            <a v-if="(route.params.user_id == 0 && props.path === props.entryPoint) || (props.path !== 'Tests.java/' && props.path !== props.entryPoint)"
                class="file-dropdown dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown"></a>
            <!-- if file -->
            <ul v-if="Object.keys(props.value).length === 0" class="dropdown-menu" data-bs-theme="light">
                <li v-if="renameAllowed"><a class="dropdown-item"
                        @click="$emit('renameFile', props.path)"><font-awesome-icon icon="fa-solid fa-pencil" fixed-width />
                        {{ $t("rename") }}</a></li>
                <li v-if="deleteAllowed"><a class="dropdown-item"
                        @click="$emit('deleteFile', props.path)"><font-awesome-icon icon="fa-solid fa-trash" fixed-width />
                        {{ $t("delete") }}</a></li>
                <li v-if="route.params.user_id == 0">
                    <a class="dropdown-item" @click="$emit('setEntryPoint', props.path)">
                        <font-awesome-icon icon="fa-solid fa-house" fixed-width /> {{ $t("set_as_entry_point") }}
                    </a>
                </li>
            </ul>
            <!-- if directory -->
            <ul v-else class="dropdown-menu" data-bs-theme="light">
                <li v-if="renameAllowed"><a class="dropdown-item" @click="$emit('renameDirectory')"><font-awesome-icon
                            icon="fa-solid fa-pencil" fixed-width /> {{ $t("rename") }}</a></li>
                <li v-if="deleteAllowed"><a class="dropdown-item" @click="$emit('deleteDirectory')"><font-awesome-icon
                            icon="fa-solid fa-trash" fixed-width /> {{ $t("delete") }}</a></li>
            </ul>
        </div>
    </li>
    <ul v-if="Object.keys(props.value).length !== 0">
        <TreeNode v-for=" [newKey, newValue]  of  Object.entries(props.value) " :entryPoint="props.entryPoint"
            :name="newKey" :value="newValue" :path="props.path + newKey + '/'" :rename-allowed="renameAllowed"
            :delete-allowed="deleteAllowed" @openFile="openFile" @renameFile="renameFile" @deleteFile="deleteFile"
            @renameDirectory="renameDirectory" @deleteDirectory="deleteDirectory" @setEntryPoint="setEntryPoint">
        </TreeNode>
    </ul>
</template>

<style scoped lang="scss">
[data-bs-theme=dark] {
    .name {
        color: lightgray;
    }

    .file-dropdown {
        background-color: #444;
    }

    .file-dropdown:hover {
        background-color: #555;
    }
}

[data-bs-theme=light] {
    .name {
        background-color: lightgray;
    }

    .file-dropdown {
        background-color: #eee;
    }

    .file-dropdown:hover {
        background-color: #ddd;
    }
}

.file-dropdown {
    border-radius: 5px;
    color: #999;
    transition: 0.2s;
}

.file-dropdown:hover {
    color: #fff;
}

ul {
    list-style: none;
}

a {
    cursor: pointer;
}

.name {
    border-radius: 5px;
    background-color: #555;
    display: inherit;
}
</style>