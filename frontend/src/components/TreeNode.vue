<script setup>
const props = defineProps({
  path: String,
  name: String,
  value: Object
})

</script>

<template>
    <li><font-awesome-icon v-if="Object.keys(props.value).length !== 0" icon="fa-solid fa-folder-open"/>
        <font-awesome-icon v-else icon="fa-solid fa-file"/> <a :href="props.path">{{ props.name }}</a></li>
    <ul v-if="Object.keys(props.value).length !== 0">
        <TreeNode v-for="[newKey, newValue] of Object.entries(props.value)" :name="newKey" :value="newValue" :path="props.path + newKey + '/'" ></TreeNode>
    </ul>
</template>

<style scoped>
ul {
    list-style: none;
}
</style>