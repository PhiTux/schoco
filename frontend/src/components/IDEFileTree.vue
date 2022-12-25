<script setup>
import { reactive, computed, watch } from "vue";

const props = defineProps(["files"]);

let state = reactive({
  files: props.files,
  test: 0,
});

function createNestedObject() {
  let f = [];
  for (const o of props.files) {
    f.push(Object.keys(o)[0]);
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
}

function printList(list, container) {
  for (const [key, value] of Object.entries(list)) {
    var li = document.createElement("li");
    li.innerHTML = key;
    if (Object.keys(value).length !== 0) {
      var fa = document.createElement("font-awesome-icon");
      fa.setAttribute("icon", "fa-solid fa-folder-open");
      li.appendChild(fa);
      var ul = document.createElement("ul");
      li.appendChild(ul);

      printList(value, ul);
      li.classList.add("treeFolder");
    } else {
      li.classList.add("treeFile");
    }
    container.appendChild(li);
  }
}

//<font-awesome-icon icon="fa-solid fa-file-circle-plus" />

watch(
  () => props.files,
  () => {
    let nestedFiles = createNestedObject();

    printList(nestedFiles, document.getElementById("root"));
  }
);
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
    <ul id="root"></ul>
  </div>
</template>

<style scoped>
.treeFolder:before {
  content: "\f07c";
  font-family: FontAwesome;
  display: inline-block;
}

ul {
  list-style: none;
}
</style>
