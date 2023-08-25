<script setup>

const props = defineProps({
    homework_id: Number,
    solution_name: String,
    solution_uuid: String,
    solution_start_showing: String,
    myProjects: Array
})
</script>

<template>
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title fs-5" id="exampleModalLabel">
                    <span v-if="solution_name === ''">Lösung hinzufügen</span>
                    <span v-else>Lösung ändern</span>
                </h1>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Homeworkid: {{ homework_id }}

                TODO: Projekt wählen: Kombi-feld aus Eingabe und Dropdown?!
                <span v-for="p of myProjects">{{ p }}</span>

                TODO: Fragen, ab wann die Lösung sichtbar sein soll. Switch ob sofort, oder Datetime wählen
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    Abbrechen
                </button>
                <button @click.prevent="addSolution()" type="button" class="btn btn-primary" data-bs-dismiss="modal">
                    Speichern
                </button>
            </div>
        </div>
    </div>
</template>