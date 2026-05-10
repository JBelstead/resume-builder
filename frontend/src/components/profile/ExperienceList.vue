<template>
  <div class="card">
    <div class="list-header">
      <h2 class="card-title">Work Experience</h2>
      <button class="btn-outline" @click="showForm = true" aria-label="Add work experience">+ Add</button>
    </div>

    <p v-if="experiences.length === 0" class="empty-msg">No work experience entries yet.</p>

    <ul v-else class="entry-list" role="list">
      <li v-for="exp in experiences" :key="exp.id" class="entry-item">
        <div class="entry-info">
          <span class="entry-primary">{{ exp.role }}</span>
          <span class="entry-secondary">{{ exp.company }}<template v-if="exp.location"> · {{ exp.location }}</template></span>
          <span class="entry-meta">
            <template v-if="exp.start_date">{{ exp.start_date.slice(0, 7) }}</template>
            –
            <template v-if="exp.end_date">{{ exp.end_date.slice(0, 7) }}</template>
            <template v-else>Present</template>
          </span>
        </div>
        <div class="entry-actions">
          <button class="btn-icon" @click="startEdit(exp)" :aria-label="`Edit ${exp.role}`">Edit</button>
          <button class="btn-icon btn-danger" @click="confirmDelete(exp)" :aria-label="`Delete ${exp.role}`">Delete</button>
        </div>
      </li>
    </ul>

    <ExperienceForm v-if="showForm" :initial="editTarget" @save="handleSave" @cancel="closeForm" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ExperienceForm from './ExperienceForm.vue'
import type { Experience } from '@/stores/profile'

defineProps<{ experiences: Experience[] }>()
const emit = defineEmits<{
  (e: 'add', data: Omit<Experience, 'id'>): void
  (e: 'update', id: number, data: Omit<Experience, 'id'>): void
  (e: 'remove', id: number): void
}>()

const showForm = ref(false)
const editTarget = ref<Experience | null>(null)

function startEdit(exp: Experience) {
  editTarget.value = exp
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editTarget.value = null
}

function handleSave(data: Omit<Experience, 'id'>) {
  if (editTarget.value?.id) {
    emit('update', editTarget.value.id, data)
  } else {
    emit('add', data)
  }
  closeForm()
}

function confirmDelete(exp: Experience) {
  if (confirm(`Delete "${exp.role}" at ${exp.company}?`)) emit('remove', exp.id!)
}
</script>

<style scoped>
.card { background: #fff; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: var(--space-6, 24px); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4, 16px); }
.card-title { font-size: var(--font-lg, 16px); font-weight: 700; }
.empty-msg { color: var(--color-muted, #6b7280); font-size: var(--font-sm, 12px); }
.entry-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: var(--space-2, 8px); }
.entry-item { display: flex; justify-content: space-between; align-items: center; padding: var(--space-3, 12px); background: #f9fafb; border-radius: 6px; }
.entry-info { display: flex; flex-direction: column; gap: 2px; }
.entry-primary { font-weight: 600; font-size: var(--font-base, 14px); }
.entry-secondary { font-size: var(--font-sm, 12px); color: var(--color-primary, #1a56db); }
.entry-meta { font-size: var(--font-xs, 10px); color: var(--color-muted, #6b7280); }
.entry-actions { display: flex; gap: var(--space-2, 8px); }
.btn-outline { background: #fff; border: 1px solid var(--color-primary, #1a56db); color: var(--color-primary, #1a56db); border-radius: 4px; padding: var(--space-1, 4px) var(--space-3, 12px); font-size: var(--font-sm, 12px); cursor: pointer; }
.btn-icon { background: none; border: 1px solid var(--color-border, #e5e7eb); border-radius: 4px; padding: 2px var(--space-2, 8px); font-size: var(--font-xs, 10px); cursor: pointer; }
.btn-danger { color: #b91c1c; border-color: #fca5a5; }
</style>
