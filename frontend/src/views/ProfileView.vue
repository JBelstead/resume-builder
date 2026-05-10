<template>
  <div class="profile-view">
    <h1 class="page-title">My Profile</h1>

    <div v-if="store.loading && !store.profile" class="loading-state" role="status" aria-live="polite">
      <div class="spinner" aria-hidden="true"></div>
      Loading profile…
    </div>

    <div v-else class="sections">
      <div v-if="store.error" class="alert-error" role="alert">{{ store.error }}</div>

      <PersonalInfoForm
        :model-value="store.profile"
        :saving="saving"
        @submit="handleProfileSave"
      />

      <EducationList
        :educations="store.educations"
        @add="(d) => store.addEducation(d)"
        @update="(id, d) => store.updateEducation(id, d)"
        @remove="(id) => store.removeEducation(id)"
      />

      <CertificationList
        :certifications="store.certifications"
        @add="(d) => store.addCertification(d)"
        @update="(id, d) => store.updateCertification(id, d)"
        @remove="(id) => store.removeCertification(id)"
      />

      <ExperienceList
        :experiences="store.experiences"
        @add="(d) => store.addExperience(d)"
        @update="(id, d) => store.updateExperience(id, d)"
        @remove="(id) => store.removeExperience(id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profile'
import type { Profile } from '@/stores/profile'
import PersonalInfoForm from '@/components/profile/PersonalInfoForm.vue'
import EducationList from '@/components/profile/EducationList.vue'
import CertificationList from '@/components/profile/CertificationList.vue'
import ExperienceList from '@/components/profile/ExperienceList.vue'

const store = useProfileStore()
const saving = ref(false)

onMounted(() => store.fetchAll())

async function handleProfileSave(data: Omit<Profile, 'id'>) {
  saving.value = true
  try {
    await store.saveProfile(data)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.profile-view { display: flex; flex-direction: column; gap: var(--space-4, 16px); }
.page-title { font-size: var(--font-2xl, 24px); font-weight: 700; margin-bottom: var(--space-2, 8px); }
.sections { display: flex; flex-direction: column; gap: var(--space-4, 16px); }
.loading-state { display: flex; align-items: center; gap: var(--space-3, 12px); color: var(--color-muted, #6b7280); }
.alert-error { background: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; border-radius: 6px; padding: var(--space-3, 12px); font-size: var(--font-sm, 12px); }
.spinner { width: 20px; height: 20px; border: 2px solid var(--color-border, #e5e7eb); border-top-color: var(--color-primary, #1a56db); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
