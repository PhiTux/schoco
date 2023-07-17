<script setup>
import { reactive } from "vue";
import NavBar from "./components/NavBar.vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

let state = reactive({
  transitionName: "fade",
});

//check if route changes from login to home or vice versa
router.afterEach((to, from) => {
  if (to.name === "login") {
    state.transitionName = "slide-left-in";
  } else if (from.name === "login") {
    state.transitionName = "slide-right-in";
  } else {
    state.transitionName = "fade";
  }
});

</script>

<template>
  <div class="app d-flex flex-column">
    <NavBar v-if="route.name !== 'ide'" />
    <div :class="{ main: route.name !== 'ide' }">
      <router-view v-slot="{ Component }">
        <Transition :name="state.transitionName" mode="out-in" appear>
          <component :is="Component" :key="$route.path" />
        </Transition>
      </router-view>
    </div>
  </div>
</template>

<style lang="scss">
/* [data-bs-theme=dark] html {
  background-color: #383838 !important;
} */

/* [data-bs-theme=light] html {
  background-color: #e0e0e0;
} */

.btn-round {
  box-shadow: 0 0 white !important;
}

body {
  overflow-x: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}

.slide-right-in-leave-active,
.slide-left-in-enter-active {
  transition: all 0.3s ease-out;
}

.slide-right-in-enter-active,
.slide-left-in-leave-active {
  transition: all 0.3s ease-in;
}

.slide-right-in-enter-from,
.slide-left-in-leave-to {
  transform: translateX(5%);
  opacity: 0;
}


.slide-right-in-leave-to,
.slide-left-in-enter-from {
  transform: translateX(-5%);
  opacity: 0;
}


:root {
  --green: #008e00;
  --green-hover: #007200;
  --green-disabled: #004700;
  --yellow: #ffd500;
  --yellow-hover: #ccaa00;
  --yellow-disabled: #806a00;
  --blue: #1b7cff;
  --blue-hover: #1662cc;
  --blue-disabled: #0e3d80;
  --indigo: #9003f7;
  --indigo-hover: #7302c6;
  --indigo-disabled: #48017b;
}

/* body {
  background-color: #383838 !important;
} */
</style>

<style scoped>
/* .app {
  color: rgb(240, 240, 240);
} */

.main {
  padding-top: 56px;
}
</style>
