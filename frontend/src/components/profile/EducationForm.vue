<template>
  <div class="modal-overlay" role="dialog" :aria-label="editing ? 'Edit education' : 'Add education'" aria-modal="true">
    <div class="modal">
      <h3 class="modal-title">{{ editing ? 'Edit Education' : 'Add Education' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="institution">Institution <span aria-hidden="true">*</span></label>
          <input id="institution" v-model="form.institution" type="text" required />
        </div>
        <div class="field">
          <label for="degree">Degree <span aria-hidden="true">*</span></label>
          <input id="degree" v-model="form.degree" type="text" required placeholder="Bachelor of Science" />
        </div>
        <div class="field">
          <label for="field">Field of Study</label>
          <input id="field" v-model="form.field_of_study" type="text" placeholder="Computer Science" />
        </div>
        <div class="field-row">
          <div class="field">
            <label for="start">Start Date</label>
            <input id="start" v-model="form.start_date" type="date" />
          </div>
          <div class="field">
            <label for="end">End Date</label>
            <input id="end" v-model="form.end_date" type="date" />
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
          <button type="submit" class="btn-primary">{{ editing ? 'Update' : 'Add' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { Education } from '@/stores/profile'

const props = defineProps<{ initial?: Education | null }>()
const emit = defineEmits<{
  (e: 'save', data: Omit<Education, 'id'>): void
  (e: 'cancel'): void
}>()

const editing = !!props.initial?.id

const form = reactive({
  institution: props.initial?.institution ?? '',
  degree: props.initial?.degree ?? '',
  field_of_study: props.initial?.field_of_study ?? '',
  start_date: props.initial?.start_date ?? '',
  end_date: props.initial?.end_date ?? '',
})

function handleSubmit() {
  emit('save', {
    institution: form.institution,
    degree: form.degree,
    field_of_study: form.field_of_study || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
  })
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; border-radius: 8px; padding: var(--space-6, 24px); width: 100%; max-width: 480px; }
.modal-title { font-size: var(--font-lg, 16px); font-weight: 700; margin-bottom: var(--space-4, 16px); }
.field { display: flex; flex-direction: column; gap: var(--space-1, 4px); margin-bottom: var(--space-3, 12px); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3, 12px); }
label { font-size: var(--font-sm, 12px); font-weight: 600; }
input { border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-3, 12px); font-size: var(--font-base, 14px); width: 100%; }
input:focus { outline: 2px solid var(--color-primary, #1a56db); outline-offset: 1px; }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-2, 8px); margin-top: var(--space-4, 16px); }
.btn-primary { background: var(--color-primary, #1a56db); color: #fff; border: none; border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); font-weight: 600; cursor: pointer; }
.btn-secondary { background: #fff; color: var(--color-text, #111928); border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); cursor: pointer; }
</style>
