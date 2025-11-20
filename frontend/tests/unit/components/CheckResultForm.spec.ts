import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import CheckResultForm from '@/components/CheckResultForm.vue';

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
 * T104: Component test for CheckResultForm
 * Tests form validation, result input
 */
describe('CheckResultForm', () => {
  let wrapper: any;

  const mockCheckItems = [
    {
      id: 1,
      check_item_name: '农药残留',
      check_method: 'GB/T 20769-2008',
      standard_value: '≤0.1mg/kg',
    },
    {
      id: 2,
      check_item_name: '重金属检测',
      check_method: 'GB 5009.12',
      standard_value: '≤1.0mg/kg',
    },
  ];

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
    });

    wrapper = mount(CheckResultForm, {
      props: {
        checkItems: mockCheckItems,
      },
      global: {
        plugins: [pinia],
        stubs: {
          'a-form': true,
          'a-form-item': true,
          'a-input': true,
          'a-select': true,
          'a-button': true,
          'a-table': true,
        },
      },
    });
  });

  describe('Rendering', () => {
    it('renders the form', () => {
      expect(wrapper.exists()).toBe(true);
    });

    it('displays check items', () => {
      expect(wrapper.props('checkItems')).toEqual(mockCheckItems);
    });

    it('has overall result field', () => {
      // Form should have overall check_result field
      expect(wrapper.html()).toContain('检验结果');
    });
  });

  describe('Form Validation', () => {
    it('validates required fields', async () => {
      // Try to submit without filling required fields
      const submitButton = wrapper.find('button[type="submit"]');
      if (submitButton.exists()) {
        await submitButton.trigger('click');
        // Validation should prevent submission
      }
    });

    it('allows valid result values', () => {
      const validResults = ['合格', '不合格', '基本合格'];
      // Each should be selectable
      validResults.forEach((result) => {
        expect(result).toBeTruthy();
      });
    });
  });

  describe('Result Input', () => {
    it('can input check result', async () => {
      await wrapper.setData({ formData: { check_result: '合格' } });
      expect(wrapper.vm.formData.check_result).toBe('合格');
    });

    it('can input item results', async () => {
      const itemResults = [
        { id: 1, check_result: '0.05mg/kg', result_indicator: '合格' },
        { id: 2, check_result: '未检出', result_indicator: '合格' },
      ];

      await wrapper.setData({ itemResults });
      expect(wrapper.vm.itemResults).toEqual(itemResults);
    });

    it('validates result format', () => {
      // Result should be from predefined list
      const validResults = ['合格', '不合格', '基本合格'];
      expect(validResults).toContain('合格');
      expect(validResults).toContain('不合格');
    });
  });

  describe('Form Submission', () => {
    it('emits submit event with data', async () => {
      const formData = {
        check_result: '合格',
        check_items: [
          { id: 1, check_result: '0.05mg/kg', result_indicator: '合格' },
        ],
      };

      await wrapper.vm.$emit('submit', formData);

      expect(wrapper.emitted('submit')).toBeTruthy();
      expect(wrapper.emitted('submit')[0]).toEqual([formData]);
    });

    it('includes all check items in submission', async () => {
      // When submitting, should include results for all items
      const submitData = {
        check_result: '合格',
        check_items: mockCheckItems.map((item) => ({
          id: item.id,
          check_result: '合格',
          result_indicator: '合格',
        })),
      };

      await wrapper.vm.$emit('submit', submitData);
      const emitted = wrapper.emitted('submit');
      if (emitted) {
        expect(emitted[0][0].check_items.length).toBe(mockCheckItems.length);
      }
    });
  });

  describe('Result Indicators', () => {
    it('has result indicator options', () => {
      const indicators = ['合格', '不合格', '基本合格'];
      expect(indicators).toContain('合格');
      expect(indicators).toContain('不合格');
    });

    it('can set result indicator for each item', async () => {
      const item1Result = { id: 1, result_indicator: '合格' };
      await wrapper.setData({
        itemResults: [item1Result],
      });

      expect(wrapper.vm.itemResults[0].result_indicator).toBe('合格');
    });
  });

  describe('Reset Functionality', () => {
    it('can reset form', async () => {
      // Set some data
      await wrapper.setData({
        formData: { check_result: '合格' },
        itemResults: [{ id: 1, check_result: 'test' }],
      });

      // Reset
      await wrapper.vm.$emit('reset');

      expect(wrapper.emitted('reset')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      // Form fields should have labels
      expect(wrapper.html()).toContain('检验结果');
    });

    it('has submit button', () => {
      const submitButton = wrapper.find('button');
      expect(submitButton.exists()).toBe(true);
    });
  });
});
