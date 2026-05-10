import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import JobDescriptionInput from '@/components/resume/JobDescriptionInput.vue'

describe('JobDescriptionInput', () => {
  it('renders text tab by default', () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
    })
    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(wrapper.find('input[type="url"]').exists()).toBe(false)
  })

  it('switches to URL input on tab click', async () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
    })
    const tabs = wrapper.findAll('[role="tab"]')
    await tabs[1].trigger('click')
    expect(wrapper.find('input[type="url"]').exists()).toBe(true)
    expect(wrapper.find('textarea').exists()).toBe(false)
  })

  it('emits submit with text payload', async () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
    })
    await wrapper.find('textarea').setValue('Python developer job')
    await wrapper.find('form').trigger('submit')
    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toMatchObject({ job_description_text: 'Python developer job' })
  })

  it('emits submit with url payload when URL tab active', async () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: false },
    })
    const tabs = wrapper.findAll('[role="tab"]')
    await tabs[1].trigger('click')
    await wrapper.find('input[type="url"]').setValue('https://example.com/job/1')
    await wrapper.find('form').trigger('submit')
    const emitted = wrapper.emitted('submit')
    expect(emitted![0][0]).toMatchObject({ job_description_url: 'https://example.com/job/1' })
  })

  it('disables submit button while submitting', () => {
    const wrapper = mount(JobDescriptionInput, {
      global: { plugins: [createPinia()] },
      props: { submitting: true },
    })
    const btn = wrapper.find('button[type="submit"]')
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
  })
})
