<template>
  <a-button
    type="primary"
    :loading="loading"
    :disabled="disabled"
    @click="handleExport"
  >
    <template #icon>
      <FileExcelOutlined />
    </template>
    导出Excel
  </a-button>
</template>

<script setup lang="ts">
/**
 * ExportButton Component
 * T147: Trigger Excel export, download file
 * T153: File download handling
 */
import { ref, computed } from 'vue';
import { message } from 'ant-design-vue';
import { FileExcelOutlined } from '@ant-design/icons-vue';
import { exportExcel, type ExportExcelParams } from '@/services/checkService';

interface Props {
  checkObjectIds?: number[];
  filters?: ExportExcelParams;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'error', error: Error): void;
}>();

const loading = ref(false);

const disabled = computed(() => {
  // Disable if no IDs and no filters
  return !props.checkObjectIds?.length && !props.filters;
});

async function handleExport() {
  loading.value = true;

  try {
    // Build export params
    const params: ExportExcelParams = {};

    if (props.checkObjectIds && props.checkObjectIds.length > 0) {
      params.check_object_ids = props.checkObjectIds;
    } else if (props.filters) {
      Object.assign(params, props.filters);
    }

    // Call API
    const blob = await exportExcel(params);

    // T153: Trigger browser download with Content-Disposition
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    // Generate filename with current date
    const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    link.download = `检测结果导出_${dateStr}.xlsx`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up blob URL
    window.URL.revokeObjectURL(url);

    message.success('导出成功');
    emit('success');
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || '导出失败';
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
