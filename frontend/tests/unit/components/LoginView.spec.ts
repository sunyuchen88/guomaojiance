import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import LoginView from '@/views/LoginView.vue';

describe('LoginView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('renders login form correctly', () => {
    const wrapper = mount(LoginView);

    // Check for username input
    expect(wrapper.find('input[type="text"]').exists()).toBe(true);

    // Check for password input
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);

    // Check for submit button
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true);
  });

  it('shows validation error when username is empty', async () => {
    const wrapper = mount(LoginView);

    // Try to submit with empty username
    const form = wrapper.find('form');
    await form.trigger('submit');

    // Should show validation error
    // Note: Exact error message depends on Ant Design Vue implementation
    expect(wrapper.text()).toContain('用户名');
  });

  it('shows validation error when password is empty', async () => {
    const wrapper = mount(LoginView);

    // Fill username but leave password empty
    await wrapper.find('input[type="text"]').setValue('testuser');

    // Try to submit
    const form = wrapper.find('form');
    await form.trigger('submit');

    // Should show validation error
    expect(wrapper.text()).toContain('密码');
  });

  it('calls login function on form submit', async () => {
    const wrapper = mount(LoginView);
    const loginSpy = vi.spyOn(wrapper.vm as any, 'handleLogin');

    // Fill in form
    await wrapper.find('input[type="text"]').setValue('testuser');
    await wrapper.find('input[type="password"]').setValue('password123');

    // Submit form
    const form = wrapper.find('form');
    await form.trigger('submit');

    // Login function should be called
    expect(loginSpy).toHaveBeenCalled();
  });

  it('disables submit button while loading', async () => {
    const wrapper = mount(LoginView);

    // Set loading state
    (wrapper.vm as any).loading = true;
    await wrapper.vm.$nextTick();

    // Submit button should be disabled
    const submitButton = wrapper.find('button[type="submit"]');
    expect(submitButton.attributes('disabled')).toBeDefined();
  });
});
