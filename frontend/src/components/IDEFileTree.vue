<script setup>
import { computed } from "vue";
import TreeNode from "./TreeNode.vue"


const emit = defineEmits(['openFile', 'renameFile', 'deleteFile', 'renameDirectory', 'deleteDirectory', 'setEntryPoint'])

const props = defineProps(["files", "renameAllowed", "deleteAllowed", "entryPoint"]);

const nestedFiles = computed(() => {
  let f = [];
  for (const o of props.files) {
    f.push(o['path']);
  }

  const output = {};
  let current;

  for (const path of f) {
    current = output;

    for (const segment of path.split("/")) {
      if (segment !== "") {
        if (!(segment in current)) {
          current[segment] = {};
        }

        current = current[segment];
      }
    }
  }

  return output;
})

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

</script>

<template>
  <div class="container" v-if="props.files.length == 0">
    <p class="placeholder-wave">
      <span class="placeholder col-12"></span>
      <span class="placeholder col-8"></span>
      <span class="placeholder col-8"></span>
      <span class="placeholder col-10"></span>
      <span class="placeholder col-12"></span>
    </p>
  </div>
  <div class="tree">
    <ul id="root">
      <TreeNode v-for="[newKey, newValue] of Object.entries(nestedFiles)" :entryPoint="props.entryPoint" :name="newKey"
        :value="newValue" :path="newKey + '/'" :renameAllowed="renameAllowed" :deleteAllowed="deleteAllowed"
        @openFile="openFile" @renameFile="renameFile" @deleteFile="deleteFile" @renameDirectory="renameDirectory"
        @deleteDirectory="deleteDirectory" @setEntryPoint="setEntryPoint">
      </TreeNode>
    </ul>
  </div>
</template>

<style scoped lang="scss">
ul {
  list-style: none;
}
</style>
