<template>
  <a-button
    type="primary"
    :loading="loading"
    :disabled="disabled"
    @click="handleSync"
  >
    <template #icon>
      <SyncOutlined />
    </template>
    获取数据
  </a-button>
</template>

<script setup lang="ts">
/**
 * DataSyncButton Component
 * T093: Trigger manual sync, show loading state
 */
import { ref } from 'vue';
import { SyncOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { fetchData, type SyncResponse } from '@/services/syncService';

interface Props {
  loading?: boolean;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
});

const emit = defineEmits<{
  (e: 'sync'): void;
  (e: 'success', result: SyncResponse): void;
  (e: 'error', error: Error): void;
}>();

const internalLoading = ref(false);

async function handleSync() {
  if (props.loading || internalLoading.value) return;

  emit('sync');
  internalLoading.value = true;

  try {
    const result = await fetchData();

    if (result.status === 'success') {
      message.success(result.message);
      emit('success', result);
    } else {
      message.error(result.message);
      emit('error', new Error(result.message));
    }
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || '同步失败';
    message.error(errorMessage);
    emit('error', error);
  } finally {
    internalLoading.value = false;
  }
}
</script>
