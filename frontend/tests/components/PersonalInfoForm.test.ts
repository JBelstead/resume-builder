import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PersonalInfoForm from '@/components/profile/PersonalInfoForm.vue'

describe('PersonalInfoForm', () => {
  it('renders all fields', () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: { modelValue: null, saving: false },
    })
    expect(wrapper.find('#name').exists()).toBe(true)
    expect(wrapper.find('#email').exists()).toBe(true)
    expect(wrapper.find('#github').exists()).toBe(true)
  })

  it('populates fields from modelValue', async () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: {
        modelValue: { name: 'Alice', email: 'alice@example.com', github_url: 'https://github.com/alice' },
        saving: false,
      },
    })
    await wrapper.vm.$nextTick()
    expect((wrapper.find('#name').element as HTMLInputElement).value).toBe('Alice')
    expect((wrapper.find('#email').element as HTMLInputElement).value).toBe('alice@example.com')
  })

  it('emits submit with form data on submit', async () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: { modelValue: null, saving: false },
    })
    await wrapper.find('#name').setValue('Bob')
    await wrapper.find('form').trigger('submit')
    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toMatchObject({ name: 'Bob' })
  })

  it('disables button while saving', () => {
    const wrapper = mount(PersonalInfoForm, {
      global: { plugins: [createPinia()] },
      props: { modelValue: null, saving: true },
    })
    const btn = wrapper.find('button[type="submit"]')
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
  })
})
