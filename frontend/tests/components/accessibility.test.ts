import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { axe, toHaveNoViolations } from 'vitest-axe'
import PersonalInfoForm from '@/components/profile/PersonalInfoForm.vue'
import JobDescriptionInput from '@/components/resume/JobDescriptionInput.vue'
import ResumeHistoryList from '@/components/resume/ResumeHistoryList.vue'

expect.extend(toHaveNoViolations)

describe('Accessibility — WCAG 2.1 AA', () => {
  it('PersonalInfoForm has no violations', async () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: { modelValue: null, saving: false },
      attachTo: document.body,
    })
    const results = await axe(wrapper.element as Element)
    expect(results).toHaveNoViolations()
    wrapper.unmount()
  })

  it('JobDescriptionInput has no violations', async () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
      attachTo: document.body,
    })
    const results = await axe(wrapper.element as Element)
    expect(results).toHaveNoViolations()
    wrapper.unmount()
  })

  it('ResumeHistoryList (empty) has no violations', async () => {
    const wrapper = mount(ResumeHistoryList, {
      global: { plugins: [createPinia()] },
      props: { resumes: [], loading: false },
      attachTo: document.body,
    })
    const results = await axe(wrapper.element as Element)
    expect(results).toHaveNoViolations()
    wrapper.unmount()
  })
})
