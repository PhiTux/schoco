<script setup>
defineProps({
  color: String,
  fontDark: Boolean,
  name: String,
  id: Number,
  isDeletable: Boolean,
  isEditable: Boolean
});
</script>

<template>
  <span class="badge rounded-pill mx-1 d-inline-flex" :style="{
    'background-color': color,
    color: fontDark ? 'var(--bs-dark)' : 'var(--bs-light)',
  }">
    <span class="align-self-center">{{ name }}</span>
    <a v-if="isEditable" class="mini-btn edit-btn" @click.prevent="$emit('edit')">
      <font-awesome-layers class="fa-lg">
        <font-awesome-icon id="background" icon="fa-circle" />
        <div style="color: var(--bs-light)">
          <font-awesome-icon class="edit-pencil" icon="fa-pencil" :style="{
              color: fontDark ? 'var(--bs-dark)' : 'var(--bs-light)'
            }" transform="shrink-4" />
        </div>
      </font-awesome-layers>
    </a>
    <a v-if="isDeletable" class="mini-btn delete-btn" @click.prevent="$emit('remove')">
      <font-awesome-layers class="fa-lg">
        <font-awesome-icon id="background" icon="fa-circle" />
        <div style="color: var(--bs-light)">
          <font-awesome-icon icon="fa-xmark" :style="{
              color: fontDark ? 'var(--bs-dark)' : 'var(--bs-light)'
            }" transform="shrink-1" />
        </div>
      </font-awesome-layers>
    </a>
  </span>
</template>

<style scoped>
.mini-btn {
  margin-left: 5px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.5);
  transition: 0.3s;
}

.badge:hover>.delete-btn {
  color: red;
}

.badge:hover>.edit-btn {
  color: yellow;
}

.badge:hover>.edit-btn>div>div>.edit-pencil {
  color: black !important;
}
</style>
