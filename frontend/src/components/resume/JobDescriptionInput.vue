<template>
  <div class="card">
    <h2 class="card-title">Generate Resume</h2>

    <div class="tabs" role="tablist" aria-label="Input method">
      <button
        role="tab"
        :aria-selected="activeTab === 'text'"
        class="tab"
        :class="{ 'tab--active': activeTab === 'text' }"
        @click="activeTab = 'text'"
      >
        Paste Text
      </button>
      <button
        role="tab"
        :aria-selected="activeTab === 'url'"
        class="tab"
        :class="{ 'tab--active': activeTab === 'url' }"
        @click="activeTab = 'url'"
      >
        Job URL
      </button>
    </div>

    <form @submit.prevent="handleSubmit">
      <div v-if="activeTab === 'text'" class="field">
        <label for="jd-text">Job Description</label>
        <textarea
          id="jd-text"
          v-model="text"
          rows="10"
          placeholder="Paste the full job description here…"
          :required="activeTab === 'text'"
        ></textarea>
      </div>

      <div v-else class="field">
        <label for="jd-url">Job Posting URL</label>
        <input
          id="jd-url"
          v-model="url"
          type="url"
          placeholder="https://example.com/jobs/software-engineer"
          :required="activeTab === 'url'"
        />
        <p class="field-hint">The URL will be fetched server-side — only this URL is contacted.</p>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="submitting">
          <span v-if="submitting" class="spinner" aria-hidden="true"></span>
          {{ submitting ? 'Generating…' : 'Generate Resume' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ submitting: boolean }>()
const emit = defineEmits<{
  (e: 'submit', payload: { job_description_text?: string; job_description_url?: string }): void
}>()

const activeTab = ref<'text' | 'url'>('text')
const text = ref('')
const url = ref('')

function handleSubmit() {
  if (activeTab.value === 'text') {
    emit('submit', { job_description_text: text.value })
  } else {
    emit('submit', { job_description_url: url.value })
  }
}
</script>

<style scoped>
.card { background: #fff; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: var(--space-6, 24px); }
.card-title { font-size: var(--font-lg, 16px); font-weight: 700; margin-bottom: var(--space-4, 16px); }
.tabs { display: flex; gap: 0; border-bottom: 2px solid var(--color-border, #e5e7eb); margin-bottom: var(--space-4, 16px); }
.tab { background: none; border: none; border-bottom: 2px solid transparent; margin-bottom: -2px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-base, 14px); cursor: pointer; color: var(--color-muted, #6b7280); font-weight: 500; }
.tab--active { color: var(--color-primary, #1a56db); border-bottom-color: var(--color-primary, #1a56db); font-weight: 700; }
.field { display: flex; flex-direction: column; gap: var(--space-1, 4px); margin-bottom: var(--space-3, 12px); }
label { font-size: var(--font-sm, 12px); font-weight: 600; }
.field-hint { font-size: var(--font-xs, 10px); color: var(--color-muted, #6b7280); margin-top: 2px; }
textarea, input[type="url"] { border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: var(--space-2, 8px) var(--space-3, 12px); font-size: var(--font-base, 14px); font-family: inherit; width: 100%; resize: vertical; }
textarea:focus, input:focus { outline: 2px solid var(--color-primary, #1a56db); outline-offset: 1px; }
.form-actions { margin-top: var(--space-4, 16px); }
.btn-primary { background: var(--color-primary, #1a56db); color: #fff; border: none; border-radius: 4px; padding: var(--space-2, 8px) var(--space-6, 24px); font-size: var(--font-base, 14px); font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: var(--space-2, 8px); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
