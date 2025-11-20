/**
 * Component tests for Export Button
 * Test T138: Test download action, loading state
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ExportButton from '@/components/ExportButton.vue';
import * as checkService from '@/services/checkService';

// Mock checkService
vi.mock('@/services/checkService', () => ({
  exportExcel: vi.fn(),
}));

// Mock message
vi.mock('ant-design-vue', () => ({
  message: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('ExportButton Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('T138.1: renders export button', () => {
    const wrapper = mount(ExportButton);

    expect(wrapper.find('button').exists()).toBe(true);
    expect(wrapper.text()).toContain('导出Excel');
  });

  it('T138.2: shows loading state when exporting', async () => {
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockImplementation(() => new Promise(() => {})); // Never resolves

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1, 2, 3],
      },
    });

    const button = wrapper.find('button');
    await button.trigger('click');
    await wrapper.vm.$nextTick();

    // Button should show loading state
    expect(wrapper.vm.loading).toBe(true);
    expect(button.attributes('disabled')).toBeDefined();
  });

  it('T138.3: calls exportExcel with check object IDs', async () => {
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1, 2, 3],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(mockExportExcel).toHaveBeenCalledWith({
      check_object_ids: [1, 2, 3],
    });
  });

  it('T138.4: calls exportExcel with query filters', async () => {
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(new Blob(['test']));

    const wrapper = mount(ExportButton, {
      props: {
        filters: {
          status: 1,
          company: '测试公司',
          start_date: '2024-01-01',
          end_date: '2024-12-31',
        },
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(mockExportExcel).toHaveBeenCalledWith({
      status: 1,
      company: '测试公司',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
    });
  });

  it('T138.5: triggers browser download on success', async () => {
    const mockBlob = new Blob(['test'], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    // Mock URL.createObjectURL and createElement
    const mockUrl = 'blob:test-url';
    global.URL.createObjectURL = vi.fn(() => mockUrl);
    global.URL.revokeObjectURL = vi.fn();

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Verify download was triggered
    expect(mockLink.href).toBe(mockUrl);
    expect(mockLink.download).toContain('.xlsx');
    expect(mockLink.click).toHaveBeenCalled();
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl);
  });

  it('T138.6: generates filename with current date', async () => {
    const mockBlob = new Blob(['test']);
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    const mockUrl = 'blob:test-url';
    global.URL.createObjectURL = vi.fn(() => mockUrl);
    global.URL.revokeObjectURL = vi.fn();

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    // Filename should contain date
    expect(mockLink.download).toMatch(/检测结果导出_\d{8}\.xlsx/);
  });

  it('T138.7: emits success event on successful export', async () => {
    const mockBlob = new Blob(['test']);
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    global.URL.createObjectURL = vi.fn(() => 'blob:test');
    global.URL.revokeObjectURL = vi.fn();

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(wrapper.emitted('success')).toBeTruthy();
  });

  it('T138.8: emits error event on export failure', async () => {
    const mockError = new Error('Export failed');
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockRejectedValue(mockError);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    const errorEvents = wrapper.emitted('error');
    expect(errorEvents).toBeTruthy();
    expect(errorEvents![0]).toEqual([mockError]);
  });

  it('T138.9: resets loading state after success', async () => {
    const mockBlob = new Blob(['test']);
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    global.URL.createObjectURL = vi.fn(() => 'blob:test');
    global.URL.revokeObjectURL = vi.fn();

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(wrapper.vm.loading).toBe(false);
  });

  it('T138.10: resets loading state after error', async () => {
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockRejectedValue(new Error('Export failed'));

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(wrapper.vm.loading).toBe(false);
  });

  it('T138.11: disables button when no data to export', () => {
    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [],
      },
    });

    const button = wrapper.find('button');
    expect(button.attributes('disabled')).toBeDefined();
  });

  it('T138.12: handles empty filters gracefully', async () => {
    const mockBlob = new Blob(['test']);
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    global.URL.createObjectURL = vi.fn(() => 'blob:test');
    global.URL.revokeObjectURL = vi.fn();

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        filters: {},
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(mockExportExcel).toHaveBeenCalledWith({});
  });

  it('T138.13: shows error message for 1000 row limit', async () => {
    const mockError = {
      response: {
        data: {
          detail: '导出数据超过1000行限制',
        },
      },
    };
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockRejectedValue(mockError);

    const { message } = await import('ant-design-vue');

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1, 2, 3],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(message.error).toHaveBeenCalledWith(expect.stringContaining('1000'));
  });

  it('T138.14: cleans up blob URL after download', async () => {
    const mockBlob = new Blob(['test']);
    const mockExportExcel = vi.mocked(checkService.exportExcel);
    mockExportExcel.mockResolvedValue(mockBlob);

    const mockUrl = 'blob:test-url';
    const mockCreateObjectURL = vi.fn(() => mockUrl);
    const mockRevokeObjectURL = vi.fn();
    global.URL.createObjectURL = mockCreateObjectURL;
    global.URL.revokeObjectURL = mockRevokeObjectURL;

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

    const wrapper = mount(ExportButton, {
      props: {
        checkObjectIds: [1],
      },
    });

    await wrapper.find('button').trigger('click');
    await flushPromises();

    expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob);
    expect(mockRevokeObjectURL).toHaveBeenCalledWith(mockUrl);
  });
});
