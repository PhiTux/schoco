<script setup>
import { computed } from "vue";
import TreeNode from "./TreeNode.vue"


const emit = defineEmits(['openFile'])

const props = defineProps(["files"]);

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

function toggleFolder(path, event) {
  console.log(path)
  console.log(event.target)
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
      <TreeNode v-for="[newKey, newValue] of Object.entries(nestedFiles)" :name="newKey" :value="newValue"
        :path="newKey + '/'" @toggleFolder="toggleFolder" @openFile="openFile"></TreeNode>
    </ul>
  </div>
</template>

<style scoped>
ul {
  list-style: none;
}
</style>
