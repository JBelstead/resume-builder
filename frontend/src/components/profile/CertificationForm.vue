<template>
  <div class="modal-overlay" role="dialog" :aria-label="editing ? 'Edit certification' : 'Add certification'" aria-modal="true">
    <div class="modal">
      <h3 class="modal-title">{{ editing ? 'Edit Certification' : 'Add Certification' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="cert-name">Name <span aria-hidden="true">*</span></label>
          <input id="cert-name" v-model="form.name" type="text" required placeholder="AWS Solutions Architect" />
        </div>
        <div class="field">
          <label for="cert-issuer">Issuer <span aria-hidden="true">*</span></label>
          <input id="cert-issuer" v-model="form.issuer" type="text" required placeholder="Amazon Web Services" />
        </div>
        <div class="field-row">
          <div class="field">
            <label for="cert-issue">Issue Date</label>
            <input id="cert-issue" v-model="form.issue_date" type="date" />
          </div>
          <div class="field">
            <label for="cert-expiry">Expiry Date</label>
            <input id="cert-expiry" v-model="form.expiry_date" type="date" />
          </div>
        </div>
        <div class="field">
          <label for="cert-id">Credential ID</label>
          <input id="cert-id" v-model="form.credential_id" type="text" />
        </div>
        <div class="field">
          <label for="cert-url">Credential URL</label>
          <input id="cert-url" v-model="form.credential_url" type="url" />
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
import type { Certification } from '@/stores/profile'

const props = defineProps<{ initial?: Certification | null }>()
const emit = defineEmits<{
  (e: 'save', data: Omit<Certification, 'id'>): void
  (e: 'cancel'): void
}>()

const editing = !!props.initial?.id
const form = reactive({
  name: props.initial?.name ?? '',
  issuer: props.initial?.issuer ?? '',
  issue_date: props.initial?.issue_date ?? '',
  expiry_date: props.initial?.expiry_date ?? '',
  credential_id: props.initial?.credential_id ?? '',
  credential_url: props.initial?.credential_url ?? '',
})

function handleSubmit() {
  emit('save', {
    name: form.name,
    issuer: form.issuer,
    issue_date: form.issue_date || null,
    expiry_date: form.expiry_date || null,
    credential_id: form.credential_id || null,
    credential_url: form.credential_url || null,
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
