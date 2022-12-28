<script setup>
const props = defineProps({
    path: String,
    name: String,
    value: Object
})

const emit = defineEmits(['openFile', 'toggleFolder'])

function openFile(path) {
    emit('openFile', path)
}

function toggleFolder(path, event) {
    emit('toggleFolder', path, event)
}

</script>

<template>
    <li class="my-2"><font-awesome-icon v-if="Object.keys(props.value).length !== 0" icon="fa-solid fa-folder-open" />
        <font-awesome-icon v-else icon="fa-solid fa-file" /> <a v-if="Object.keys(props.value).length === 0"
            @click="$emit('openFile', props.path)">
            <div class="px-1">{{ props.name }}</div>
        </a>
        <a v-else @click="$emit('toggleFolder', props.path, $event)">
            <div class="px-1">{{ props.name }}</div>
        </a>
        <!-- <div v-else class="px-1">{{ props.name }}</div> -->
    </li>
    <ul v-if="Object.keys(props.value).length !== 0">
        <TreeNode v-for="[newKey, newValue] of Object.entries(props.value)" :name="newKey" :value="newValue"
            :path="props.path + newKey + '/'" @toggleFolder="toggleFolder" @openFile="openFile"></TreeNode>
    </ul>
</template>

<style scoped>
ul {
    list-style: none;
}

a {
    cursor: pointer;
}

div {
    border-radius: 5px;
    background-color: #555;
    display: inherit;
}
</style>