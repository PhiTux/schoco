<script setup>
import { onBeforeMount } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

onBeforeMount(() => {
  console.log(route.params);
});
</script>

<template>
  <h1>IDE</h1>
</template>
