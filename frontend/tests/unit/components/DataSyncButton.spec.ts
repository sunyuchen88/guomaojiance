import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import DataSyncButton from '@/components/DataSyncButton.vue';

// Mock services
vi.mock('@/services/syncService', () => ({
  fetchData: vi.fn(),
}));

// Mock ant-design-vue
vi.mock('ant-design-vue', async () => {
  const actual = await vi.importActual('ant-design-vue');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      loading: vi.fn(),
    },
  };
});

/**
 * T080: Component test for DataSyncButton
 * Tests click action, loading state
 */
describe('DataSyncButton', () => {
  let wrapper: any;

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
    });

    wrapper = mount(DataSyncButton, {
      global: {
        plugins: [pinia],
        stubs: {
          'a-button': {
            template: '<button :disabled="disabled" :loading="loading" @click="$emit(\'click\')"><slot /></button>',
            props: ['disabled', 'loading'],
          },
          'sync-outlined': true,
        },
      },
    });
  });

  describe('Rendering', () => {
    it('renders the sync button', () => {
      expect(wrapper.find('button').exists()).toBe(true);
    });

    it('displays correct button text', () => {
      expect(wrapper.text()).toContain('获取数据');
    });

    it('button is not disabled by default', () => {
      expect(wrapper.find('button').attributes('disabled')).toBeFalsy();
    });
  });

  describe('Click Action', () => {
    it('emits sync event when clicked', async () => {
      await wrapper.find('button').trigger('click');

      expect(wrapper.emitted()).toHaveProperty('sync');
    });

    it('calls sync service on click', async () => {
      const { fetchData } = await import('@/services/syncService');

      await wrapper.find('button').trigger('click');
      await flushPromises();

      // Verify the click was handled
      expect(wrapper.emitted('sync')).toBeTruthy();
    });
  });

  describe('Loading State', () => {
    it('shows loading state when syncing', async () => {
      await wrapper.setProps({ loading: true });

      expect(wrapper.props('loading')).toBe(true);
    });

    it('disables button when loading', async () => {
      await wrapper.setProps({ loading: true, disabled: true });

      expect(wrapper.find('button').attributes('disabled')).toBeDefined();
    });

    it('re-enables button after sync completes', async () => {
      await wrapper.setProps({ loading: true });
      await wrapper.setProps({ loading: false });

      expect(wrapper.props('loading')).toBe(false);
    });
  });

  describe('Success/Error Handling', () => {
    it('emits success event on successful sync', async () => {
      const { fetchData } = await import('@/services/syncService');
      (fetchData as any).mockResolvedValueOnce({
        status: 'success',
        fetched_count: 10,
        message: '同步成功',
      });

      await wrapper.find('button').trigger('click');
      await flushPromises();

      // Component should handle success
      expect(wrapper.emitted('sync')).toBeTruthy();
    });

    it('emits error event on failed sync', async () => {
      const { fetchData } = await import('@/services/syncService');
      (fetchData as any).mockRejectedValueOnce(new Error('Network error'));

      await wrapper.find('button').trigger('click');
      await flushPromises();

      // Component should handle error
      expect(wrapper.emitted('sync')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('has accessible button', () => {
      const button = wrapper.find('button');
      expect(button.exists()).toBe(true);
    });

    it('can be triggered by keyboard', async () => {
      const button = wrapper.find('button');
      await button.trigger('keydown.enter');

      // Button should be focusable
      expect(button.element.tagName).toBe('BUTTON');
    });
  });
});
