<script setup>
const props = defineProps({
    path: String,
    name: String,
    value: Object,
    renameAllowed: Boolean,
    deleteAllowed: Boolean,
})

const emit = defineEmits(['openFile', 'toggleFolder', 'renameFile', 'deleteFile', 'renameDirectory', 'deleteDirectory'])

function openFile(path) {
    emit('openFile', path)
}

function toggleFolder(path, event) {
    emit('toggleFolder', path, event)
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

</script>

<template>
    <li class="my-2">
        <font-awesome-icon v-if="Object.keys(props.value).length !== 0" icon="fa-solid fa-folder-open" class="mx-1 treeItem"
            fixed-width />
        <font-awesome-icon v-else icon="fa-solid fa-file" class="mx-1 treeItem" fixed-width />
        <div class="btn-group">
            <a v-if="Object.keys(props.value).length === 0" @click="$emit('openFile', props.path)">
                <div class="name px-1">{{ props.name }}</div>
            </a>
            <a v-else @click="$emit('toggleFolder', props.path, $event)">
                <div class="name px-1">{{ props.name }}</div>
            </a>
            <a v-if="props.path !== 'Schoco.java/' && props.path !== 'Tests.java/'"
                class="file-dropdown dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown"></a>
            <!-- if file -->
            <ul v-if="Object.keys(props.value).length === 0" class="dropdown-menu" data-bs-theme="light">
                <li v-if="renameAllowed"><a class="dropdown-item"
                        @click="$emit('renameFile', props.path)"><font-awesome-icon icon="fa-solid fa-pencil" fixed-width />
                        Umbenennen</a></li>
                <li v-if="deleteAllowed"><a class="dropdown-item"
                        @click="$emit('deleteFile', props.path)"><font-awesome-icon icon="fa-solid fa-trash" fixed-width />
                        Löschen</a></li>
            </ul>
            <!-- if directory -->
            <ul v-else class="dropdown-menu" data-bs-theme="light">
                <li v-if="renameAllowed"><a class="dropdown-item" @click="$emit('renameDirectory')"><font-awesome-icon
                            icon="fa-solid fa-pencil" fixed-width /> Umbenennen</a></li>
                <li v-if="deleteAllowed"><a class="dropdown-item" @click="$emit('deleteDirectory')"><font-awesome-icon
                            icon="fa-solid fa-trash" fixed-width /> Löschen</a></li>
            </ul>
        </div>
    </li>
    <ul v-if="Object.keys(props.value).length !== 0">
        <TreeNode v-for="[newKey, newValue] of Object.entries(props.value)" :name="newKey" :value="newValue"
            :path="props.path + newKey + '/'" :rename-allowed="renameAllowed" :delete-allowed="deleteAllowed"
            @toggleFolder="toggleFolder" @openFile="openFile" @renameFile="renameFile" @deleteFile="deleteFile"
            @renameDirectory="renameDirectory" @deleteDirectory="deleteDirectory">
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