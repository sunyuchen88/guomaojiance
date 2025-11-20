import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import Antd from 'ant-design-vue';

/**
 * Mount a component with default plugins and options
 */
export function mountWithPlugins(component: any, options: any = {}) {
  const pinia = createPinia();

  return mount(component, {
    global: {
      plugins: [pinia, Antd],
      ...options.global,
    },
    ...options,
  });
}

/**
 * Create a mock router
 */
export function createMockRouter() {
  return {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    currentRoute: {
      value: {
        path: '/',
        name: 'Dashboard',
        params: {},
        query: {},
      },
    },
  };
}

/**
 * Wait for async updates
 */
export async function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}
