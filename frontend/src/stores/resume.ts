import { defineStore } from 'pinia'
import { ref } from 'vue'
import { resumeApi } from '@/services/api'
import type { AxiosError } from 'axios'

export interface ResumeListItem {
  id: number
  job_title: string | null
  company_name: string | null
  created_at: string
}

export interface ResumeCreateResponse {
  id: number
  job_title: string | null
  company_name: string | null
  created_at: string
}

export type GenerateStatus = 'idle' | 'loading' | 'success' | 'error'

function extractErrorMessage(err: unknown, defaultMsg = 'An error occurred'): string {
  const axiosErr = err as AxiosError<{ detail: string }>
  return axiosErr.response?.data?.detail ?? defaultMsg
}

export const useResumeStore = defineStore('resume', () => {
  const status = ref<GenerateStatus>('idle')
  const error = ref<string | null>(null)
  const lastResume = ref<ResumeCreateResponse | null>(null)
  const history = ref<ResumeListItem[]>([])
  const historyLoading = ref(false)

  async function generate(payload: { job_description_text?: string; job_description_url?: string }) {
    status.value = 'loading'
    error.value = null
    lastResume.value = null
    try {
      const res = await resumeApi.generate(payload)
      lastResume.value = res.data
      status.value = 'success'
      return res.data
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail: string }>
      const statusCode = axiosErr.response?.status
      if (statusCode === 400) {
        error.value = axiosErr.response?.data?.detail ?? 'Profile not complete'
      } else if (statusCode === 504) {
        error.value = 'The AI took too long to respond. Please try again.'
      } else if (statusCode === 502) {
        error.value = 'AI service is unavailable. Make sure Ollama is running.'
      } else if (statusCode === 422) {
        error.value = axiosErr.response?.data?.detail ?? 'Invalid job description or URL'
      } else {
        error.value = 'Failed to generate resume'
      }
      status.value = 'error'
      throw err
    }
  }

  async function fetchHistory() {
    historyLoading.value = true
    try {
      const res = await resumeApi.list()
      history.value = res.data
    } catch {
      // non-fatal; keep whatever is already in history
    } finally {
      historyLoading.value = false
    }
  }

  function downloadResume(id: number) {
    window.open(resumeApi.downloadUrl(id), '_blank')
  }

  async function deleteResume(id: number) {
    await resumeApi.remove(id)
    history.value = history.value.filter((r) => r.id !== id)
    if (lastResume.value?.id === id) {
      lastResume.value = null
      status.value = 'idle'
    }
  }

  function reset() {
    status.value = 'idle'
    error.value = null
    lastResume.value = null
  }

  return {
    status,
    error,
    lastResume,
    history,
    historyLoading,
    generate,
    fetchHistory,
    downloadResume,
    deleteResume,
    reset,
  }
})
