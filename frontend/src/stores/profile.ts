import { defineStore } from 'pinia'
import { ref } from 'vue'
import { profileApi, educationApi, certificationsApi, experienceApi } from '@/services/api'
import type { AxiosError } from 'axios'

export interface Profile {
  id?: number
  name: string
  email?: string | null
  phone?: string | null
  github_url?: string | null
  linkedin_url?: string | null
  website_url?: string | null
}

export interface Education {
  id?: number
  institution: string
  degree: string
  field_of_study?: string | null
  start_date?: string | null
  end_date?: string | null
  gpa?: string | null
  description?: string | null
}

export interface Certification {
  id?: number
  name: string
  issuer: string
  issue_date?: string | null
  expiry_date?: string | null
  credential_id?: string | null
  credential_url?: string | null
}

export interface Experience {
  id?: number
  company: string
  role: string
  start_date?: string | null
  end_date?: string | null
  location?: string | null
  description?: string | null
  skills?: string | null
}

function extractErrorMessage(err: unknown): string {
  const axiosErr = err as AxiosError<{ detail: string }>
  return axiosErr.response?.data?.detail ?? 'An error occurred'
}

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<Profile | null>(null)
  const educations = ref<Education[]>([])
  const certifications = ref<Certification[]>([])
  const experiences = ref<Experience[]>([])

  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const [profileRes, eduRes, certRes, expRes] = await Promise.allSettled([
        profileApi.get(),
        educationApi.list(),
        certificationsApi.list(),
        experienceApi.list(),
      ])
      if (profileRes.status === 'fulfilled') profile.value = profileRes.value.data
      else if ((profileRes.reason as AxiosError)?.response?.status !== 404) {
        error.value = 'Failed to load profile'
      }
      if (eduRes.status === 'fulfilled') educations.value = eduRes.value.data
      if (certRes.status === 'fulfilled') certifications.value = certRes.value.data
      if (expRes.status === 'fulfilled') experiences.value = expRes.value.data
    } finally {
      loading.value = false
    }
  }

  async function saveProfile(data: Omit<Profile, 'id'>) {
    loading.value = true
    error.value = null
    try {
      const res = await profileApi.upsert(data)
      profile.value = res.data
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addEducation(data: Omit<Education, 'id'>) {
    const res = await educationApi.create(data)
    educations.value.push(res.data)
    return res.data
  }

  async function updateEducation(id: number, data: Partial<Education>) {
    const res = await educationApi.update(id, data)
    const idx = educations.value.findIndex((e) => e.id === id)
    if (idx !== -1) educations.value[idx] = res.data
    return res.data
  }

  async function removeEducation(id: number) {
    await educationApi.remove(id)
    educations.value = educations.value.filter((e) => e.id !== id)
  }

  async function addCertification(data: Omit<Certification, 'id'>) {
    const res = await certificationsApi.create(data)
    certifications.value.push(res.data)
    return res.data
  }

  async function updateCertification(id: number, data: Partial<Certification>) {
    const res = await certificationsApi.update(id, data)
    const idx = certifications.value.findIndex((c) => c.id === id)
    if (idx !== -1) certifications.value[idx] = res.data
    return res.data
  }

  async function removeCertification(id: number) {
    await certificationsApi.remove(id)
    certifications.value = certifications.value.filter((c) => c.id !== id)
  }

  async function addExperience(data: Omit<Experience, 'id'>) {
    const res = await experienceApi.create(data)
    experiences.value.push(res.data)
    return res.data
  }

  async function updateExperience(id: number, data: Partial<Experience>) {
    const res = await experienceApi.update(id, data)
    const idx = experiences.value.findIndex((e) => e.id === id)
    if (idx !== -1) experiences.value[idx] = res.data
    return res.data
  }

  async function removeExperience(id: number) {
    await experienceApi.remove(id)
    experiences.value = experiences.value.filter((e) => e.id !== id)
  }

  return {
    profile,
    educations,
    certifications,
    experiences,
    loading,
    error,
    fetchAll,
    saveProfile,
    addEducation,
    updateEducation,
    removeEducation,
    addCertification,
    updateCertification,
    removeCertification,
    addExperience,
    updateExperience,
    removeExperience,
  }
})
