<template>
  <a-button
    type="default"
    :loading="loading"
    :disabled="disabled"
    @click="handleDownload"
  >
    <template #icon>
      <DownloadOutlined />
    </template>
    报告下载
  </a-button>
</template>

<script setup lang="ts">
/**
 * BatchDownloadButton Component
 * 需求2.4: 批量下载检测报告PDF
 * 支持多维度筛选后批量下载所有匹配的报告
 */
import { ref, computed } from 'vue';
import { message } from 'ant-design-vue';
import { DownloadOutlined } from '@ant-design/icons-vue';
import { batchDownloadReports, type BatchDownloadParams } from '@/services/checkService';

interface Props {
  filters?: BatchDownloadParams;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'error', error: Error): void;
}>();

const loading = ref(false);

const disabled = computed(() => {
  // Disable if no filters provided
  return !props.filters;
});

async function handleDownload() {
  loading.value = true;

  try {
    // Build download params from filters
    const params: BatchDownloadParams = {};

    if (props.filters) {
      Object.assign(params, props.filters);
    }

    // Call API
    const blob = await batchDownloadReports(params);

    // Trigger browser download
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    // Generate filename with current date/time
    const dateStr = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
    link.download = `reports_batch_${dateStr}.zip`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up blob URL
    window.URL.revokeObjectURL(url);

    message.success('报告批量下载成功');
    emit('success');
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || '批量下载失败';
    message.error(errorMessage);
    emit('error', error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>
