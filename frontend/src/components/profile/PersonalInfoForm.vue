<template>
  <form class="card" @submit.prevent="handleSubmit" aria-label="Personal information form">
    <h2 class="card-title">Personal Information</h2>

    <div class="field">
      <label for="name">Full Name <span aria-hidden="true">*</span></label>
      <input id="name" v-model="form.name" type="text" required placeholder="Jane Smith" />
    </div>

    <div class="field-row">
      <div class="field">
        <label for="email">Email</label>
        <input id="email" v-model="form.email" type="email" placeholder="jane@example.com" />
      </div>
      <div class="field">
        <label for="phone">Phone</label>
        <input id="phone" v-model="form.phone" type="tel" placeholder="+1 555 000 0000" />
      </div>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="github">GitHub URL</label>
        <input id="github" v-model="form.github_url" type="url" placeholder="https://github.com/username" />
      </div>
      <div class="field">
        <label for="linkedin">LinkedIn URL</label>
        <input id="linkedin" v-model="form.linkedin_url" type="url" placeholder="https://linkedin.com/in/username" />
      </div>
    </div>

    <div class="field">
      <label for="website">Website URL</label>
      <input id="website" v-model="form.website_url" type="url" placeholder="https://yoursite.com" />
    </div>

    <div class="form-actions">
      <button type="submit" class="btn-primary" :disabled="saving">
        <span v-if="saving" class="spinner" aria-hidden="true"></span>
        {{ saving ? 'Saving…' : 'Save Profile' }}
      </button>
      <span v-if="saved" class="success-msg" role="status">Saved!</span>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { Profile } from '@/stores/profile'

const props = defineProps<{ modelValue: Profile | null; saving: boolean }>()
const emit = defineEmits<{ (e: 'submit', payload: Omit<Profile, 'id'>): void }>()

const form = reactive({
  name: '',
  email: '',
  phone: '',
  github_url: '',
  linkedin_url: '',
  website_url: '',
})

const saved = ref(false)

watch(
  () => props.modelValue,
  (p) => {
    if (p) {
      form.name = p.name ?? ''
      form.email = p.email ?? ''
      form.phone = p.phone ?? ''
      form.github_url = p.github_url ?? ''
      form.linkedin_url = p.linkedin_url ?? ''
      form.website_url = p.website_url ?? ''
    }
  },
  { immediate: true },
)

function handleSubmit() {
  saved.value = false
  emit('submit', {
    name: form.name,
    email: form.email || null,
    phone: form.phone || null,
    github_url: form.github_url || null,
    linkedin_url: form.linkedin_url || null,
    website_url: form.website_url || null,
  })
  setTimeout(() => { saved.value = true }, 50)
}
</script>

<style scoped>
.card { background: #fff; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: var(--space-6, 24px); }
.card-title { font-size: var(--font-lg, 16px); font-weight: 700; margin-bottom: var(--space-4, 16px); }
.field { display: flex; flex-direction: column; gap: var(--space-1, 4px); margin-bottom: var(--space-3, 12px); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3, 12px); }
label { font-size: var(--font-sm, 12px); font-weight: 600; color: var(--color-text, #111928); }
input { border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-3, 12px); font-size: var(--font-base, 14px); width: 100%; }
input:focus { outline: 2px solid var(--color-primary, #1a56db); outline-offset: 1px; }
.form-actions { display: flex; align-items: center; gap: var(--space-3, 12px); margin-top: var(--space-4, 16px); }
.btn-primary { background: var(--color-primary, #1a56db); color: #fff; border: none; border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: var(--space-2, 8px); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.success-msg { color: #065f46; font-size: var(--font-sm, 12px); font-weight: 600; }
.spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
