<template>
  <div class="card">
    <h2 class="card-title">Resume History</h2>

    <div v-if="loading" class="loading-row" role="status" aria-live="polite">
      <span class="spinner" aria-hidden="true"></span> Loading history…
    </div>

    <p v-else-if="resumes.length === 0" class="empty-msg">No resumes generated yet.</p>

    <div v-else class="table-wrap">
      <table class="history-table" aria-label="Past resumes">
        <thead>
          <tr>
            <th scope="col">Job Title</th>
            <th scope="col">Company</th>
            <th scope="col">Generated</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="resume in resumes" :key="resume.id">
            <td>{{ resume.job_title ?? '—' }}</td>
            <td>{{ resume.company_name ?? '—' }}</td>
            <td>{{ formatDate(resume.created_at) }}</td>
            <td class="actions-cell">
              <button
                class="btn-action"
                @click="emit('download', resume.id)"
                :aria-label="`Download resume ${resume.id}`"
              >
                Download
              </button>
              <button
                class="btn-action btn-danger"
                @click="confirmDelete(resume)"
                :aria-label="`Delete resume ${resume.id}`"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ResumeListItem } from '@/stores/resume'

defineProps<{ resumes: ResumeListItem[]; loading: boolean }>()
const emit = defineEmits<{
  (e: 'download', id: number): void
  (e: 'delete', id: number): void
}>()

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function confirmDelete(resume: ResumeListItem) {
  const label = resume.job_title ?? `Resume #${resume.id}`
  if (confirm(`Delete "${label}"? This cannot be undone.`)) {
    emit('delete', resume.id)
  }
}
</script>

<style scoped>
.card { background: #fff; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: var(--space-6, 24px); }
.card-title { font-size: var(--font-lg, 16px); font-weight: 700; margin-bottom: var(--space-4, 16px); }
.loading-row { display: flex; align-items: center; gap: var(--space-2, 8px); color: var(--color-muted, #6b7280); font-size: var(--font-sm, 12px); }
.empty-msg { color: var(--color-muted, #6b7280); font-size: var(--font-sm, 12px); }
.table-wrap { overflow-x: auto; }
.history-table { width: 100%; border-collapse: collapse; font-size: var(--font-sm, 12px); }
.history-table th { text-align: left; padding: var(--space-2, 8px) var(--space-3, 12px); border-bottom: 2px solid var(--color-border, #e5e7eb); font-weight: 700; color: var(--color-muted, #6b7280); text-transform: uppercase; font-size: var(--font-xs, 10px); letter-spacing: 0.5px; }
.history-table td { padding: var(--space-2, 8px) var(--space-3, 12px); border-bottom: 1px solid var(--color-border, #e5e7eb); vertical-align: middle; }
.history-table tr:last-child td { border-bottom: none; }
.actions-cell { display: flex; gap: var(--space-2, 8px); align-items: center; }
.btn-action { background: none; border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: 2px var(--space-2, 8px); font-size: var(--font-xs, 10px); cursor: pointer; white-space: nowrap; }
.btn-danger { color: #b91c1c; border-color: #fca5a5; }
.spinner { width: 14px; height: 14px; border: 2px solid var(--color-border, #e5e7eb); border-top-color: var(--color-primary, #1a56db); border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
