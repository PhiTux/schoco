<script setup>
defineProps({
  color: String,
  fontDark: Boolean,
  name: String,
  id: Number,
  isDeletable: Boolean,
});
</script>

<template>
  <span class="badge rounded-pill mx-1" :style="{
    'background-color': color,
    color: fontDark ? 'var(--bs-dark)' : 'var(--bs-light)',
  }">{{ name }}
    <a v-if="isDeletable" class="mini-btn" @click.prevent="$emit('remove')"><font-awesome-icon icon="fa-xmark" :style="{
      color: fontDark ? 'var(--bs-dark)' : 'var(--bs-light)',
    }" /></a></span>
</template>

<style scoped>
.mini-btn {
  cursor: pointer;
}
</style>
