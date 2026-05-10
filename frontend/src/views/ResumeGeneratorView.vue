<template>
  <div class="generator-view">
    <h1 class="page-title">Generate Resume</h1>

    <div v-if="!profileStore.profile && !profileStore.loading" class="alert-warning" role="alert">
      <strong>Profile not found.</strong>
      <RouterLink to="/" class="alert-link">Complete your profile</RouterLink> before generating a resume.
    </div>

    <JobDescriptionInput
      :submitting="resumeStore.status === 'loading'"
      @submit="handleGenerate"
    />

    <!-- Success panel -->
    <div v-if="resumeStore.status === 'success' && resumeStore.lastResume" class="success-panel" role="status">
      <div class="success-icon" aria-hidden="true">✓</div>
      <div class="success-content">
        <p class="success-title">Resume generated!</p>
        <p class="success-meta">
          <template v-if="resumeStore.lastResume.job_title">{{ resumeStore.lastResume.job_title }}</template>
          <template v-if="resumeStore.lastResume.company_name"> at {{ resumeStore.lastResume.company_name }}</template>
        </p>
        <button
          class="btn-download"
          @click="resumeStore.downloadResume(resumeStore.lastResume.id)"
        >
          Download PDF
        </button>
      </div>
    </div>

    <!-- Error panel -->
    <div v-if="resumeStore.status === 'error'" class="alert-error" role="alert">
      {{ resumeStore.error }}
    </div>

    <ResumeHistoryList
      :resumes="resumeStore.history"
      :loading="resumeStore.historyLoading"
      @download="(id) => resumeStore.downloadResume(id)"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useResumeStore } from '@/stores/resume'
import JobDescriptionInput from '@/components/resume/JobDescriptionInput.vue'
import ResumeHistoryList from '@/components/resume/ResumeHistoryList.vue'

const profileStore = useProfileStore()
const resumeStore = useResumeStore()

onMounted(async () => {
  if (!profileStore.profile) await profileStore.fetchAll()
  await resumeStore.fetchHistory()
})

async function handleGenerate(payload: { job_description_text?: string; job_description_url?: string }) {
  await resumeStore.generate(payload)
  if (resumeStore.status === 'success') {
    await resumeStore.fetchHistory()
  }
}

async function handleDelete(id: number) {
  await resumeStore.deleteResume(id)
  await resumeStore.fetchHistory()
}
</script>

<style scoped>
.generator-view { display: flex; flex-direction: column; gap: var(--space-4, 16px); }
.page-title { font-size: var(--font-2xl, 24px); font-weight: 700; margin-bottom: var(--space-2, 8px); }
.alert-warning { background: #fffbeb; border: 1px solid #fcd34d; color: #92400e; border-radius: 6px; padding: var(--space-3, 12px) var(--space-4, 16px); font-size: var(--font-sm, 12px); display: flex; gap: var(--space-2, 8px); align-items: center; }
.alert-link { color: var(--color-primary, #1a56db); font-weight: 600; text-decoration: underline; }
.alert-error { background: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; border-radius: 6px; padding: var(--space-3, 12px) var(--space-4, 16px); font-size: var(--font-sm, 12px); }
.success-panel { display: flex; align-items: center; gap: var(--space-4, 16px); background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: var(--space-4, 16px) var(--space-6, 24px); }
.success-icon { width: 32px; height: 32px; background: #16a34a; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; }
.success-title { font-weight: 700; font-size: var(--font-base, 14px); color: #14532d; }
.success-meta { font-size: var(--font-sm, 12px); color: #166534; }
.btn-download { margin-top: var(--space-2, 8px); background: #16a34a; color: #fff; border: none; border-radius: 4px; padding: var(--space-2, 8px) var(--space-4, 16px); font-size: var(--font-sm, 12px); font-weight: 600; cursor: pointer; }
</style>
