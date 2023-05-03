<script setup>
const props = defineProps({
    path: String,
    name: String,
    value: Object
})

const emit = defineEmits(['openFile', 'toggleFolder', 'renameFile'])

function openFile(path) {
    emit('openFile', path)
}

function toggleFolder(path, event) {
    emit('toggleFolder', path, event)
}

function renameFile(path) {
    emit('renameFile', path)
}

</script>

<template>
    <li class="my-2">
        <font-awesome-icon v-if="Object.keys(props.value).length !== 0" icon="fa-solid fa-folder-open" class="mx-1" />
        <font-awesome-icon v-else icon="fa-solid fa-file" class="mx-1" />
        <div class="btn-group">
            <a v-if="Object.keys(props.value).length === 0" @click="$emit('openFile', props.path)">
                <div class="name px-1">{{ props.name }}</div>
            </a>
            <a v-else @click="$emit('toggleFolder', props.path, $event)">
                <div class="name px-1">{{ props.name }}</div>
            </a>
            <a v-if="props.path !== 'Schoco.java/' && props.path !== 'Tests.java/'"
                class="file-dropdown dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown"></a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" @click="$emit('renameFile', props.path)"><font-awesome-icon
                            icon="fa-solid fa-pencil" fixed-width /> Umbenennen</a></li>
                <li><a class="dropdown-item"><font-awesome-icon icon="fa-solid fa-trash" fixed-width /> Löschen</a></li>
            </ul>
        </div>
        <!-- <div v-else class="px-1">{{ props.name }}</div> -->
    </li>
    <ul v-if="Object.keys(props.value).length !== 0">
        <TreeNode v-for="[newKey, newValue] of Object.entries(props.value)" :name="newKey" :value="newValue"
            :path="props.path + newKey + '/'" @toggleFolder="toggleFolder" @openFile="openFile" @renameFile="renameFile">
        </TreeNode>
    </ul>
</template>

<style scoped>
.file-dropdown {
    border-radius: 5px;
    background-color: #444;
    color: #999;
    transition: 0.2s;
}

.file-dropdown:hover {
    background-color: #555;
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