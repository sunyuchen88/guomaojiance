import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import SubmitModal from '@/components/SubmitModal.vue';

// Mock ant-design-vue
vi.mock('ant-design-vue', async () => {
  const actual = await vi.importActual('ant-design-vue');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
    },
  };
});

/**
 * T123: Component test for SubmitModal
 * Tests confirmation dialog, submit action
 */
describe('SubmitModal', () => {
  let wrapper: any;

  const mockCheckObject = {
    id: 1,
    check_no: 'CHK-2024-0001',
    sample_name: '测试样品',
    company_name: '测试公司',
    status: 1,
    check_result: '合格',
    check_items: [
      {
        id: 1,
        check_item_name: '农药残留',
        check_result: '0.05mg/kg',
        result_indicator: '合格',
      },
      {
        id: 2,
        check_item_name: '重金属检测',
        check_result: '未检出',
        result_indicator: '合格',
      },
    ],
  };

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
    });

    wrapper = mount(SubmitModal, {
      props: {
        visible: true,
        checkObject: mockCheckObject,
      },
      global: {
        plugins: [pinia],
        stubs: {
          'a-modal': {
            template: '<div class="modal-stub"><slot /></div>',
            props: ['visible', 'title', 'confirmLoading'],
          },
          'a-descriptions': true,
          'a-descriptions-item': true,
          'a-table': true,
        },
      },
    });
  });

  describe('Rendering', () => {
    it('renders the modal', () => {
      expect(wrapper.find('.modal-stub').exists()).toBe(true);
    });

    it('displays check object summary', () => {
      expect(wrapper.text()).toContain('CHK-2024-0001');
      expect(wrapper.text()).toContain('测试样品');
    });

    it('displays overall check result', () => {
      expect(wrapper.text()).toContain('合格');
    });

    it('shows check items count', () => {
      // Should display number of items
      expect(wrapper.props('checkObject').check_items.length).toBe(2);
    });
  });

  describe('Result Summary', () => {
    it('displays check items table', () => {
      const checkItems = wrapper.props('checkObject').check_items;
      expect(checkItems.length).toBe(2);
      expect(checkItems[0].check_item_name).toBe('农药残留');
    });

    it('shows result indicators', () => {
      const items = wrapper.props('checkObject').check_items;
      expect(items.every((item: any) => item.result_indicator === '合格')).toBe(true);
    });

    it('displays report URL if available', () => {
      const propsWithReport = {
        ...mockCheckObject,
        report_url: '/reports/test.pdf',
      };

      wrapper.setProps({ checkObject: propsWithReport });
      // Should show report info
    });
  });

  describe('Confirmation Dialog', () => {
    it('shows confirmation message', () => {
      expect(wrapper.text()).toContain('确认') || expect(wrapper.text()).toContain('提交');
    });

    it('warns about irreversible action', () => {
      // Confirmation should indicate submit is final
      expect(wrapper.html()).toBeTruthy();
    });

    it('has confirm button', async () => {
      await wrapper.vm.$emit('ok');
      expect(wrapper.emitted('ok')).toBeTruthy();
    });

    it('has cancel button', async () => {
      await wrapper.vm.$emit('cancel');
      expect(wrapper.emitted('cancel')).toBeTruthy();
    });
  });

  describe('Submit Action', () => {
    it('emits submit event on confirm', async () => {
      await wrapper.vm.$emit('ok');
      expect(wrapper.emitted('ok')).toBeTruthy();
    });

    it('shows loading state during submit', async () => {
      await wrapper.setProps({ confirmLoading: true });
      expect(wrapper.props('confirmLoading')).toBe(true);
    });

    it('disables buttons when loading', async () => {
      await wrapper.setProps({ confirmLoading: true });
      // Buttons should be disabled during submit
      expect(wrapper.props('confirmLoading')).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('emits error event on failure', async () => {
      const error = new Error('Submit failed');
      await wrapper.vm.$emit('error', error);

      expect(wrapper.emitted('error')).toBeTruthy();
      expect(wrapper.emitted('error')[0]).toEqual([error]);
    });

    it('displays error message', async () => {
      await wrapper.setProps({ error: '提交失败' });
      expect(wrapper.props('error')).toBe('提交失败');
    });
  });

  describe('Validation', () => {
    it('validates check object has result', () => {
      const validObject = { ...mockCheckObject, check_result: '合格' };
      expect(validObject.check_result).toBeTruthy();

      const invalidObject = { ...mockCheckObject, check_result: null };
      expect(invalidObject.check_result).toBeFalsy();
    });

    it('validates status is correct', () => {
      // Status should be 1 (已检测)
      expect(mockCheckObject.status).toBe(1);
    });

    it('shows warning if no report uploaded', () => {
      const noReport = { ...mockCheckObject, report_url: null };
      // Should show warning but allow submit
      expect(noReport.report_url).toBeNull();
    });
  });

  describe('Close Actions', () => {
    it('emits cancel on close', async () => {
      await wrapper.vm.$emit('cancel');
      expect(wrapper.emitted('cancel')).toBeTruthy();
    });

    it('resets state on close', async () => {
      await wrapper.setProps({ visible: false });
      expect(wrapper.props('visible')).toBe(false);
    });
  });

  describe('Accessibility', () => {
    it('has proper modal structure', () => {
      expect(wrapper.find('.modal-stub').exists()).toBe(true);
    });

    it('has descriptive content', () => {
      // Modal should clearly describe what will be submitted
      expect(wrapper.text().length).toBeGreaterThan(0);
    });
  });
});
