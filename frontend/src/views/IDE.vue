<script setup>
import { onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import CodeService from "../services/code.service";

const route = useRoute();

onBeforeMount(() => {
  console.log("loading " + route.params.project_uuid);

  CodeService.loadAllFiles(route.params.project_uuid).then(
    (response) => {
      console.log(response.data);
    },
    (error) => {}
  );
});
</script>

<template>
  <h1>IDE</h1>
</template>
