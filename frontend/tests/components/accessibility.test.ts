import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { axe } from 'vitest-axe'
import PersonalInfoForm from '@/components/profile/PersonalInfoForm.vue'
import JobDescriptionInput from '@/components/resume/JobDescriptionInput.vue'
import ResumeHistoryList from '@/components/resume/ResumeHistoryList.vue'

type AxeResults = { violations: { id: string; description: string }[] }

describe('Accessibility — WCAG 2.1 AA', () => {
  it('PersonalInfoForm has no violations', async () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: { modelValue: null, saving: false },
      attachTo: document.body,
    })
    const results = (await axe(wrapper.element as Element)) as AxeResults
    expect(results.violations).toHaveLength(0)
    wrapper.unmount()
  })

  it('JobDescriptionInput has no violations', async () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
      attachTo: document.body,
    })
    const results = (await axe(wrapper.element as Element)) as AxeResults
    expect(results.violations).toHaveLength(0)
    wrapper.unmount()
  })

  it('ResumeHistoryList (empty) has no violations', async () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: [], loading: false },
      attachTo: document.body,
    })
    const results = (await axe(wrapper.element as Element)) as AxeResults
    expect(results.violations).toHaveLength(0)
    wrapper.unmount()
  })
})
