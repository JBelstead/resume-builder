<template>
  <div class="modal-overlay" role="dialog" :aria-label="editing ? 'Edit experience' : 'Add experience'" aria-modal="true">
    <div class="modal">
      <h3 class="modal-title">{{ editing ? 'Edit Experience' : 'Add Experience' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="field-row">
          <div class="field">
            <label for="exp-company">Company <span aria-hidden="true">*</span></label>
            <input id="exp-company" v-model="form.company" type="text" required />
          </div>
          <div class="field">
            <label for="exp-role">Role / Title <span aria-hidden="true">*</span></label>
            <input id="exp-role" v-model="form.role" type="text" required />
          </div>
        </div>
        <div class="field">
          <label for="exp-location">Location</label>
          <input id="exp-location" v-model="form.location" type="text" placeholder="Remote, New York, NY…" />
        </div>
        <div class="field-row">
          <div class="field">
            <label for="exp-start">Start Date</label>
            <input id="exp-start" v-model="form.start_date" type="date" />
          </div>
          <div class="field">
            <label for="exp-end">End Date</label>
            <input id="exp-end" v-model="form.end_date" type="date" :disabled="current" />
          </div>
        </div>
        <div class="field checkbox-field">
          <label>
            <input type="checkbox" v-model="current" @change="onCurrentToggle" />
            Current position (no end date)
          </label>
        </div>
        <div class="field">
          <label for="exp-desc">Description</label>
          <textarea id="exp-desc" v-model="form.description" rows="3" placeholder="Key responsibilities and achievements…"></textarea>
        </div>
        <div class="field">
          <label for="exp-skills">Skills (comma-separated)</label>
          <input id="exp-skills" v-model="form.skills" type="text" placeholder="Python, FastAPI, Docker" />
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
import { reactive, ref } from 'vue'
import type { Experience } from '@/stores/profile'

const props = defineProps<{ initial?: Experience | null }>()
const emit = defineEmits<{
  (e: 'save', data: Omit<Experience, 'id'>): void
  (e: 'cancel'): void
}>()

const editing = !!props.initial?.id
const current = ref(!props.initial?.end_date && !!props.initial?.id)

const form = reactive({
  company: props.initial?.company ?? '',
  role: props.initial?.role ?? '',
  location: props.initial?.location ?? '',
  start_date: props.initial?.start_date ?? '',
  end_date: props.initial?.end_date ?? '',
  description: props.initial?.description ?? '',
  skills: props.initial?.skills ?? '',
})

function onCurrentToggle() {
  if (current.value) form.end_date = ''
}

function handleSubmit() {
  emit('save', {
    company: form.company,
    role: form.role,
    location: form.location || null,
    start_date: form.start_date || null,
    end_date: current.value ? null : form.end_date || null,
    description: form.description || null,
    skills: form.skills || null,
  })
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; overflow-y: auto; padding: var(--space-4, 16px); }
.modal { background: #fff; border-radius: 8px; padding: var(--space-6, 24px); width: 100%; max-width: 520px; }
.modal-title { font-size: var(--font-lg, 16px); font-weight: 700; margin-bottom: var(--space-4, 16px); }
.field { display: flex; flex-direction: column; gap: var(--space-1, 4px); margin-bottom: var(--space-3, 12px); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3, 12px); }
.checkbox-field { flex-direction: row; align-items: center; gap: var(--space-2, 8px); }
label { font-size: var(--font-sm, 12px); font-weight: 600; }
input, textarea { border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-3, 12px); font-size: var(--font-base, 14px); width: 100%; font-family: inherit; }
input:focus, textarea:focus { outline: 2px solid var(--color-primary, #1a56db); outline-offset: 1px; }
input:disabled { background: #f9fafb; color: var(--color-muted, #6b7280); }
.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-2, 8px); margin-top: var(--space-4, 16px); }
.btn-primary { background: var(--color-primary, #1a56db); color: #fff; border: none; border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); font-weight: 600; cursor: pointer; }
.btn-secondary { background: #fff; color: var(--color-text, #111928); border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); cursor: pointer; }
</style>
