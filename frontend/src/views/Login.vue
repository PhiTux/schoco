<script setup>
import { reactive, computed, onMounted, onBeforeMount } from "vue";
import { useAuthStore } from "../stores/auth.store.js";
import UserService from "../services/user.service.js";
import { useRoute, useRouter } from "vue-router";
import { Toast } from "bootstrap";
import { version } from "../../package.json"
import PasswordInput from "../components/PasswordInput.vue"
import PasswordInfo from "../components/PasswordInfo.vue"

const router = useRouter();

const state = reactive({
  loginIncomplete: false,
  registerIncomplete: false,
  showLoginError: false,
  showRegistrationSuccess: false,
  backendVersion: "",
  showRegistrationError: false,
  showRegistrationErrorMessage: false,
  registrationErrorMessage: "",
});

const login = reactive({
  username: "",
  password: "",
})

const register = reactive({
  teacherKey: "",
  name: "",
  username: "",
  password1: "",
  password2: "",
})

onBeforeMount(() => {
  UserService.getVersion().then(
    (response) => {
      state.backendVersion = response.data
    }, (error) => {
      console.log(error.response)
      state.backendVersion = "unknown"
    }
  )
})

onMounted(() => {
  let route = useRoute()
  if (route.query.token_expired) {
    const toast = new Toast(
      document.getElementById("toastTokenExpiredError")
    );
    toast.show();
  }
  router.replace({ query: {} });

  document.title = "Login"
})

async function loginUser() {
  if (!loginValid.value) {
    state.loginIncomplete = true;
    return;
  }
  const authStore = useAuthStore();
  const result = await authStore.login(
    login.username,
    login.password
  );
  if (result && result.response.status == 401) {
    state.loginIncomplete = false;
    state.showLoginError = true;
  }
}

function registerTeacher() {
  if (
    !registerValid.value ||
    !registerPasswordsEqual.value ||
    registerPasswordTooShort.value
  ) {
    state.registerIncomplete = true;
    return;
  }
  UserService.registerTeacher(
    register.teacherKey,
    register.name,
    register.username,
    register.password1
  ).then(
    (response) => {
      if (response.data) {
        state.showRegistrationErrorMessage = false;
        state.showRegistrationSuccess = true;
        state.showRegistrationError = false;
      } else {
        state.showRegistrationErrorMessage = false;
        state.showRegistrationError = true;
        state.showRegistrationSuccess = false;
      }

    },
    (error) => {
      state.registrationErrorMessage = error.response.data.detail;
      state.showRegistrationError = true;
      state.showRegistrationSuccess = false;
      state.showRegistrationErrorMessage = true;
    }
  );
}

const registerValid = computed(() => {
  let tmp =
    register.teacherKey !== "" &&
    register.name !== "" &&
    register.username !== "" &&
    register.password1 !== "" &&
    register.password2 !== "";
  if (tmp) state.registerIncomplete = false;
  return tmp;
});

const loginValid = computed(() => {
  var tmp = login.username !== "" && login.password !== "";
  if (tmp) state.loginIncomplete = false;
  return tmp;
});

const registerPasswordsEqual = computed(() => {
  return register.password1 === register.password2;
});

const registerPasswordTooShort = computed(() => {
  return (
    register.password1.length > 0 && register.password1.length < 8
  );
});
</script>

<template>
  <div>
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast align-items-center text-bg-danger border-0" id="toastTokenExpiredError" role="alert"
        aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            {{ $t("token_expired") }}
          </div>
        </div>
      </div>
    </div>
    <div class="center-fix d-flex flex-column">
      <!-- begin github animated corner https://github.com/eugena/github-animated-corners/ --><a target="_blank"
        href="https://github.com/phitux/schoco" class="github-corner" aria-label="View source on GitHub"
        title="View source on GitHub"><svg xmlns="http://www.w3.org/2000/svg" style="position: absolute; right: 0"
          viewBox="0 0 250 250" fill="#151513" height="80" width="80">
          <path fill="#fff" class="octo-background"
            d="M 249.57771,250.29409 C 163.6834,162.06673 87.406263,88.122635 -0.4222853,0.29408743 H 249.57771 Z"></path>
          <path fill="currentColor"
            d="m 194.57892,71.296301 c -2,-4 -5.00268,-7.999511 -9.00269,-11.999515 -3.99999,-3.999997 -7.9995,-7.002681 -11.9995,-9.002681 -4.00001,-14.000002 -8.99659,-16.998292 -8.99659,-16.998292 -8,3.999999 -11.00464,8.998533 -11.00462,10.998545 -6.00001,0 -10.99732,2.000735 -15.99732,7.000731 -16,16.000004 -10.00195,29.997316 -2.00195,40.997318 -3,0 -6.99854,0.998782 -10.99855,4.998771 L 113.57917,109.2968 c -2,1 -5.99975,-1.00097 -5.99975,-1.00097 l 26.99584,26.99584 c 0,0 -1.99999,-3.99877 0,-4.99877 l 14.00147,-14.00147 c 2.00001,-3 3.00294,-5.9956 3.00293,-7.9956 11,8 23.99732,14.99804 40.99732,-2.00195 5,-5.00001 7.00073,-9.997326 7.00073,-15.997325 -0.90398,-9.744341 -2.80609,-14.23012 -4.99878,-19.000243 z">
          </path>
          <path fill="currentColor" class="octo-arm"
            d="m 121.28633,101.84712 c -14.99999,-9.000009 -8.99999,-19.00001 -8.99999,-19.00001 2.99999,-6.999997 1.99999,-10.999997 1.99999,-10.999997 -1,-7.000002 3,-1.999998 3,-1.999998 4.00001,4.999996 2,11 2,11 -2.99999,9.999998 5.00001,14.999998 9,15.999996"
            style="transform-origin: 130px 106px;"></path>
          <path fill="currentColor"
            d="m 210.61601,77.354548 c 0,0 -2.99732,-5.000738 -15.99732,-7.000737 -0.0144,-0.02843 0.007,0.01428 0,0 -0.007,-0.01428 -3.99055,0.468874 -3.99055,0.468874 l 5.4469,19.797551 3.57294,-1.284473 c 2.01561,-1.004006 6.98378,-3.016688 10.96801,-11.981199 z"
            style="transform-origin:180px 90px;"></path>
          <path fill="#fff" class="octo-face"
            d="m 157.89355,66.610672 c -3.6953,-3.732717 -7.91112,-5.499913 -12.18983,-5.109056 -4.40252,0.402191 -7.13979,2.856546 -7.87463,3.598819 -7.07601,7.147691 -5.83073,16.6566 3.50711,26.774603 1.74973,1.898424 3.65469,3.889989 5.66306,5.91869 1.98876,2.008926 3.9938,3.970152 5.96079,5.829492 11.66194,11.03287 19.88339,7.51635 24.72642,2.62392 4.69996,-4.74761 6.92511,-12.647837 -0.93566,-20.588227 -0.19312,-0.195097 -0.5156,-0.479793 -1.31843,-1.179779 -1.71474,-1.495896 -4.90485,-4.280358 -7.8452,-7.250494 -3.2474,-3.28029 -6.32518,-6.797215 -8.16252,-8.899526 -0.85763,-0.980686 -1.27935,-1.464133 -1.5311,-1.718439 z">
          </path>
          <path fill="currentColor"
            d="m 152.14888,95.779316 c -0.16786,-0.167854 -0.4399,-0.167678 -0.60757,-6e-6 -0.66926,0.669255 -2.20394,0.630882 -3.25661,-0.42178 -0.15188,-0.151888 -0.28137,-0.314719 -0.39094,-0.484545 -0.27436,-0.424649 -0.42501,-0.891266 -0.49172,-1.329545 -0.0135,-0.08772 -0.0233,-0.174308 -0.0303,-0.259131 -0.021,-0.254464 -0.0144,-0.493507 0.0111,-0.702245 0.0423,-0.347542 0.13665,-0.610438 0.24371,-0.717497 0.16767,-0.167672 0.16785,-0.439717 0,-0.607563 -0.16785,-0.167854 -0.43989,-0.167672 -0.60756,-10e-7 -0.0866,0.08662 -0.16552,0.201023 -0.23441,0.337652 -0.10292,0.205165 -0.18327,0.460877 -0.23241,0.749235 -0.0491,0.288359 -0.0669,0.609536 -0.0456,0.945785 0.0215,0.336058 0.0827,0.68736 0.19117,1.036157 0.13593,0.435767 0.34628,0.867413 0.6472,1.260503 0.10041,0.130907 0.21071,0.257691 0.33174,0.37874 0.63088,0.63088 1.38245,0.973575 2.10837,1.079738 0.10362,0.01503 0.20695,0.02546 0.30898,0.03102 0.20444,0.01112 0.40511,0.0038 0.59878,-0.02134 0.48383,-0.06276 0.92265,-0.235099 1.26338,-0.498709 0.0681,-0.05273 0.13235,-0.109022 0.19225,-0.168918 0.16821,-0.167853 0.16803,-0.439896 3.6e-4,-0.607565 z">
          </path>
          <path fill="currentColor"
            d="m 150.73021,91.109058 c -0.0362,0.186498 -0.0362,0.378735 -1e-5,0.565239 0.0136,0.06995 0.0323,0.139166 0.0559,0.206948 0.0473,0.135574 0.11495,0.265587 0.20318,0.385376 0.0441,0.05986 0.0933,0.117281 0.14741,0.171438 0.21663,0.21663 0.48382,0.352203 0.76376,0.406177 0.11656,0.0226 0.23528,0.0312 0.35364,0.02547 0.16462,-0.0079 0.32512,-0.05326 0.48042,-0.116025 0.17878,-0.07228 0.34969,-0.17072 0.49477,-0.315797 0.57779,-0.577797 0.57797,-1.514792 1.7e-4,-2.092591 -0.28889,-0.288894 -0.66745,-0.433252 -1.04638,-0.433072 -0.0165,-2.1e-5 -0.0328,0.0041 -0.0495,0.0047 -0.11132,0.0038 -0.22129,0.02224 -0.3296,0.05093 -0.15191,0.04033 -0.29984,0.09899 -0.43505,0.188298 -0.0821,0.05414 -0.15976,0.117478 -0.23203,0.189747 -0.0723,0.07227 -0.13539,0.150099 -0.18975,0.232033 -0.10864,0.163937 -0.18076,0.34467 -0.21699,0.53117 z">
          </path>
          <path fill="currentColor"
            d="m 153.95489,72.39001 c 0.0493,-0.477547 0.0511,-0.942374 0.004,-1.387104 -0.047,-0.444739 -0.14239,-0.869748 -0.28818,-1.266958 -0.1458,-0.397217 -0.34162,-0.767704 -0.5891,-1.103409 -0.12374,-0.167853 -0.26038,-0.327093 -0.41012,-0.476837 -2.39512,-2.395112 -7.23017,-1.443235 -10.79953,2.126122 -3.56935,3.569358 -4.11631,7.999491 -1.72119,10.394606 0.14974,0.149737 0.30737,0.288005 0.47235,0.414605 0.32979,0.253392 0.68845,0.460702 1.07059,0.621912 0.38197,0.161042 0.78725,0.276167 1.21047,0.34467 0.42286,0.0685 0.86365,0.09074 1.31645,0.06653 0.45263,-0.02439 0.91728,-0.09522 1.38836,-0.212683 1.64857,-0.411202 3.37497,-1.394461 4.93656,-2.956058 1.56159,-1.561594 2.62232,-3.365455 3.12085,-5.101364 0.14275,-0.496019 0.23905,-0.986486 0.28836,-1.464038 z">
          </path>
          <path fill="currentColor"
            d="m 176.11077,91.594139 c -2.39512,-2.395112 -7.23018,-1.44324 -10.79954,2.126118 -3.56935,3.569358 -4.11648,7.999323 -1.72119,10.394613 2.39529,2.3953 6.82524,1.84816 10.3946,-1.72119 3.56937,-3.569367 4.52142,-8.404245 2.12613,-10.799541 z"
            style="transform-origin: 170px 100px;"></path>
        </svg>
      </a><!-- end github animated corner -->
      <div class="container-fluid flex-fill align-items-center d-flex justify-content-center">
        <div class="w-100 row text-center align-items-center">
          <div class="col-xxl-1"></div>
          <div class="col-xs-12 col-lg-6 col-xxl-4">
            <div class="container-lg mb-5">
              <div class="schoco-icon">{🍫}</div>
              SCHOCO<br />
              <b><u>SCH</u></b>ool <b><u>O</u></b>nline <b><u>CO</u></b>ding
            </div>
          </div>
          <div class="col-xs-12 col-lg-6 col-xxl-4">
            <div class="accordion" id="loginAccordion">
              <div class="accordion-item">
                <h2 class="accordion-header" id="headingOne">
                  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne"
                    aria-expanded="true" aria-controls="collapseOne">
                    {{ $t("login") }}
                  </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne"
                  data-bs-parent="#loginAccordion">
                  <div class="accordion-body">
                    <form @submit.prevent="loginUser()">
                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-user" fixed-width /></span>
                        <div class="form-floating">
                          <input type="text" id="floatingInputLogin" class="form-control" v-model="login.username"
                            placeholder="Username" autofocus />
                          <label for="floatingInputLogin">{{ $t("username") }}</label>
                        </div>
                      </div>

                      <PasswordInput v-model="login.password" :description="$t('password')" />

                      <div v-if="state.loginIncomplete" class="alert alert-danger" role="alert">
                        {{ $t("input_incomplete") }}
                      </div>
                      <div v-if="state.showLoginError" class="alert alert-danger" role="alert">
                        {{ $t("show_login_error") }}
                      </div>

                      <button class="btn btn-primary" :class="{ disabled: !loginValid }">
                        {{ $t("login") }}
                      </button>
                    </form>
                  </div>
                </div>
              </div>
              <div class="accordion-item">
                <h2 class="accordion-header" id="headingTwo">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                    data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                    {{ $t("registration_only_for_teachers") }}
                  </button>
                </h2>
                <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo"
                  data-bs-parent="#loginAccordion">
                  <div class="accordion-body">
                    <form @submit.prevent="registerTeacher()">
                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-lock" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input type="password" id="floatingInputTeacherKey" class="form-control"
                            v-model="register.teacherKey" placeholder="" />
                          <label for="floatingInputTeacherKey">{{ $t("teacher_key") }}</label>
                        </div>
                      </div>

                      <hr />

                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-signature" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input :disabled="register.teacherKey == ''" type="text" id="floatingInputRegisterName"
                            class="form-control" v-model="register.name" placeholder="" />
                          <label for="floatingInputRegisterName">{{ $t("full_name") }}</label>
                        </div>
                      </div>

                      <div class="input-group mb-3">
                        <span class="input-group-text" id="basic-addon1">
                          <font-awesome-icon icon="fa-solid fa-user" fixed-width />
                        </span>
                        <div class="form-floating">
                          <input :disabled="register.teacherKey == ''" type="text" id="floatingInputRegister"
                            class="form-control" v-model="register.username" placeholder="" />
                          <label for="floatingInputRegister">{{ $t("username") }}</label>
                        </div>
                      </div>

                      <hr />

                      <PasswordInfo />

                      <PasswordInput :disabled="register.teacherKey === ''" v-model="register.password1"
                        :description="$t('password')" />

                      <PasswordInput :disabled="register.teacherKey === ''" v-model="register.password2"
                        :description="$t('password')" />

                      <div v-if="state.registerIncomplete" class="alert alert-danger" role="alert">
                        {{ $t("input_incomplete") }}
                      </div>
                      <div v-if="!registerPasswordsEqual" class="alert alert-danger" role="alert">
                        {{ $t("passwords_not_identical") }}
                      </div>
                      <div v-if="registerPasswordTooShort" class="alert alert-danger" role="alert">
                        {{ $t("password_at_least_8") }}
                      </div>
                      <div v-if="state.showRegistrationSuccess" class="alert alert-success" role="alert">
                        {{ $t("registration_successful") }}
                      </div>
                      <div v-if="state.showRegistrationError" class="alert alert-danger" role="alert">
                        <span v-if="state.showRegistrationErrorMessage">{{ $t("error_msg") }}: {{
                          state.registrationErrorMessage }}<br><br></span>
                        {{ $t("registration_error") }}
                      </div>

                      <button class="btn btn-primary" :class="{
                        disabled: !registerValid || registerPasswordTooShort,
                      }">
                        {{ $t("register") }}
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-xxl-3"></div>
        </div>
        <div class="position-absolute bottom-0 end-0">
          <a href="https://hub.docker.com/r/phitux/schoco-backend/tags">Backend: {{ state.backendVersion }}</a><br />
          <a href="https://hub.docker.com/r/phitux/schoco-nginx/tags">Frontend: {{ version }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
$fill: #fff;
$color: #24292e;
$fill2: #151513;

[data-bs-theme=light] {
  .github-corner {
    fill: $color;
    color: $fill;
  }

  .octo-background,
  .octo-face {
    fill: $color;
  }
}

[data-bs-theme=dark] {
  .github-corner {
    fill: $fill;
    color: $color;
  }

  .octo-background,
  .octo-face {
    fill: $fill;
  }
}


.github-corner:hover .octo-face {
  display: inline;
}

.github-corner .octo-face {
  display: none;
}

.github-corner:hover .octo-arm {
  animation: octocat-wave 560ms ease-in-out;
}

@keyframes octocat-wave {

  0%,
  100% {
    transform: rotate(0deg);
  }

  20%,
  60% {
    transform: rotate(-25deg);
  }

  40%,
  80% {
    transform: rotate(10deg);
  }
}

@media (max-width: 500px) {
  .github-corner:hover .octo-arm {
    animation: none;
  }

  .github-corner .octo-arm {
    animation: octocat-wave 560ms ease-in-out;
  }
}

.greyButton {
  text-decoration: none;
  color: inherit;
}

.schoco-icon {
  font-size: 80px;
}

.center-fix {
  height: calc(100vh - 56px);
}
</style>
