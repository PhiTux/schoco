<script setup>
import PasswordInput from "../components/PasswordInput.vue"
import PasswordInfo from "../components/PasswordInfo.vue"
import UserService from "../services/user.service.js"
import { useAuthStore } from "../stores/auth.store.js";
import { reactive, onMounted, computed } from "vue"
import { useI18n } from 'vue-i18n'
import { Toast } from "bootstrap"
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const i18n = useI18n()
const router = useRouter();

const state = reactive({
    oldPassword: "",
    newPassword1: "",
    newPassword2: "",
    passwordInvalidResponse: false,
    isChangingPassword: false
})

onMounted(() => {
    document.title = i18n.t("change_password")
    document.getElementById("chpwd1").focus()
})

const passwordInvalid = computed(() => {
    return state.newPassword1.length < 8
        || !passwordsEqual.value
})

const passwordTooShort = computed(() => {
    return state.newPassword1.length > 0 && state.newPassword1.length < 8
})

const passwordsEqual = computed(() => {
    return state.newPassword1 === state.newPassword2
})

function changePassword() {
    if (passwordInvalid.value || state.isChangingPassword) return;

    state.passwordInvalidResponse = false;
    state.isChangingPassword = true;

    UserService.changePassword(state.oldPassword, state.newPassword1).then(
        (response) => {
            state.isChangingPassword = false;

            const toast = new Toast(
                document.getElementById("toastChangePasswordSuccess")
            );
            toast.show();

            // set password changed
            authStore.setPasswordChanged();

            // continue to home
            router.push("/home")
        },
        (error) => {
            state.isChangingPassword = false;
            console.log(error.response)

            if (error.response.status === 401) {
                state.passwordInvalidResponse = true;
                return;
            }

            const toast = new Toast(
                document.getElementById("toastChangePasswordError")
            );
            toast.show();
        }
    )
}

</script>

<template>
    <div>
        <div class="toast-container position-fixed bottom-0 end-0 p-3">
            <div class="toast align-items-center text-bg-danger border-0" id="toastChangePasswordError" role="alert"
                aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        {{ $t("error_changing_password") }}
                    </div>
                </div>
            </div>

            <div class="toast align-items-center text-bg-success border-0" id="toastChangePasswordSuccess" role="alert"
                aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        {{ $t("success_changing_password") }}
                    </div>
                </div>
            </div>
        </div>
        <div class="container p-3 mt-5 rounded">
            <h2 class="text-center mb-4">{{ $t('change_password') }}</h2>

            <form @submit.prevent="changePassword()">
                <PasswordInput v-model="state.oldPassword" :description="$t('current_password')" id="chpwd1" />
            </form>
            <PasswordInfo />

            <form @submit.prevent="changePassword()">
                <PasswordInput v-model="state.newPassword1" :description="$t('new_password')" id="chpwd2" />
            </form>
            <form @submit.prevent="changePassword()">
                <PasswordInput v-model="state.newPassword2" :description="$t('new_password')" id="chpwd3" />
            </form>

            <div v-if="passwordTooShort" class="alert alert-danger" role="alert">
                {{ $t("password_at_least_8") }}
            </div>

            <div v-if="!passwordsEqual" class="alert alert-danger" role="alert">
                {{ $t("passwords_not_identical") }}
            </div>

            <div v-if="state.passwordInvalidResponse" class="alert alert-danger" role="alert"
                v-html="$t('password_change_invalid')" />

            <div class="d-flex flex-row justify-content-between">
                <button class="btn btn-sm btn-danger me-2" @click="authStore.logout()"><font-awesome-icon
                        icon="fa-solid fa-xmark" fixed-width /> {{ $t('logout') }}</button>
                <button class="btn btn-primary ms-2" @click="changePassword">
                    <span v-if="!state.isChangingPassword"><font-awesome-icon icon="fa-solid fa-check" fixed-width /> {{
                        $t("change_password") }}</span>
                    <div v-else class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.container {
    max-width: 500px;
    box-shadow: 0 0 20px rgb(78, 78, 78);
    transition: 0.3s;
}

.container:hover {
    box-shadow: 0 0 30px rgb(78, 78, 78);
}
</style>