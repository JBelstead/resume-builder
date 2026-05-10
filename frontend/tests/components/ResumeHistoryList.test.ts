import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import ResumeHistoryList from '@/components/resume/ResumeHistoryList.vue'
import type { ResumeListItem } from '@/stores/resume'

const sampleResumes: ResumeListItem[] = [
  { id: 1, job_title: 'Backend Engineer', company_name: 'Acme', created_at: '2026-01-15T10:00:00Z' },
  { id: 2, job_title: null, company_name: null, created_at: '2026-02-20T12:00:00Z' },
]

describe('ResumeHistoryList', () => {
  it('shows empty message when no resumes', () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: [], loading: false },
    })
    expect(wrapper.text()).toContain('No resumes generated')
  })

  it('shows loading state', () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: [], loading: true },
    })
    expect(wrapper.text()).toContain('Loading history')
  })

  it('renders resume rows', () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: sampleResumes, loading: false },
    })
    expect(wrapper.text()).toContain('Backend Engineer')
    expect(wrapper.text()).toContain('Acme')
  })

  it('emits download event', async () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: sampleResumes, loading: false },
    })
    const downloadBtns = wrapper.findAll('button').filter((b) => b.text() === 'Download')
    await downloadBtns[0].trigger('click')
    expect(wrapper.emitted('download')).toBeTruthy()
    expect(wrapper.emitted('download')![0][0]).toBe(1)
  })

  it('emits delete event after confirmation', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true))
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: sampleResumes, loading: false },
    })
    const deleteBtns = wrapper.findAll('button').filter((b) => b.text() === 'Delete')
    await deleteBtns[0].trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')![0][0]).toBe(1)
  })
})
