<template>
  <a-button
    :loading="loading"
    :disabled="disabled"
    @click="handleDownload"
  >
    <template #icon>
      <DownloadOutlined />
    </template>
    下载报告
  </a-button>
</template>

<script setup lang="ts">
/**
 * DownloadButton Component
 * T148: Trigger PDF download
 * T154: Disable button if no report URL
 */
import { ref, computed } from 'vue';
import { message } from 'ant-design-vue';
import { DownloadOutlined } from '@ant-design/icons-vue';
import { downloadReport } from '@/services/checkService';

interface Props {
  checkNo?: string;
  reportUrl?: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'error', error: Error): void;
}>();

const loading = ref(false);

// T154: Disable button if no report URL
const disabled = computed(() => {
  return !props.reportUrl || !props.checkNo;
});

async function handleDownload() {
  if (!props.checkNo) {
    message.error('检测编号不存在');
    return;
  }

  if (!props.reportUrl) {
    message.error('该样品暂无报告文件');
    return;
  }

  loading.value = true;

  try {
    // Call API to download report
    const blob = await downloadReport(props.checkNo);

    // Trigger browser download
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${props.checkNo}_report.pdf`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up blob URL
    window.URL.revokeObjectURL(url);

    message.success('下载成功');
    emit('success');
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || '下载失败';
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
