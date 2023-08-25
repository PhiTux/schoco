<script setup>
import { reactive } from "vue";

const props = defineProps({
    modelValue: String,
    description: String,
    disabled: Boolean,
    id: String
});

defineEmits(['update:modelValue'])

let state = reactive({
    showPassword: false
})

function hidePassword() {
    state.showPassword = false;
}

function showPassword() {
    state.showPassword = true;
}

</script>

<template>
    <div class="input-group mb-3">
        <span class="input-group-text" id="basic-addon1"><font-awesome-icon icon="fa-solid fa-key" fixed-width /></span>
        <div class="form-floating">
            <input :type="[
                state.showPassword ? 'text' : 'password',
            ]" :id="id" class="form-control" :placeholder="description" :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)" :disabled="disabled" />
            <label :for="id">{{ description }}</label>
        </div>
        <span class="input-group-text" id="basic-addon1">
            <a class="greyButton" @mousedown="showPassword()" @mouseup="hidePassword()" @mouseleave="hidePassword()">
                <font-awesome-icon v-if="!state.showPassword" icon="fa-solid fa-eye-slash" fixed-width />
                <font-awesome-icon v-else icon="fa-solid fa-eye" fixed-width />
            </a>
        </span>
    </div>
</template>

<style scoped>
.greyButton {
    text-decoration: none;
    color: inherit;
}
</style>