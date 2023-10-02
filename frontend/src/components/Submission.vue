<script setup>
import { computed } from 'vue';

const props = defineProps({
    submission: String
});


const result = computed(() => {
    if (props.submission === undefined || props.submission.length === 0) {
        return 0;
    }

    const submission = JSON.parse(props.submission);
    let passed_tests = submission.passed_tests;
    let failed_tests = submission.failed_tests;
    return (passed_tests / (passed_tests + failed_tests)) * 100;

});

</script>

<template>
    <span :class="{ red: result < 50, yellow: result >= 50 && result < 100, green: result == 100 }">
        {{ result }}
    </span>
</template>

<style scoped>
.red {
    color: red;
}

.yellow {
    color: darkorange;
}

.green {
    color: green;
}
</style>