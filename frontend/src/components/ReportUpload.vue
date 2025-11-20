<template>
  <div class="report-upload">
    <a-upload
      v-model:file-list="fileList"
      :before-upload="beforeUpload"
      :custom-request="handleUpload"
      :max-count="1"
      accept=".pdf,application/pdf"
      :disabled="disabled || uploading"
    >
      <a-button :loading="uploading" :disabled="disabled">
        <template #icon>
          <UploadOutlined />
        </template>
        上传PDF报告
      </a-button>
    </a-upload>

    <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <a-progress :percent="uploadProgress" />
    </div>

    <div v-if="error" class="upload-error">
      <a-alert :message="error" type="error" closable @close="error = ''" />
    </div>

    <div v-if="uploadedFileUrl" class="uploaded-file">
      <a-alert
        message="文件上传成功"
        :description="`文件地址: ${uploadedFileUrl}`"
        type="success"
        closable
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ReportUpload Component
 * T114: PDF file upload with progress indicator
 */
import { ref } from 'vue';
import { UploadOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import type { UploadFile, UploadProps } from 'ant-design-vue';

interface Props {
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

const emit = defineEmits<{
  (e: 'success', data: { file_url: string; filename: string }): void;
  (e: 'error', error: Error): void;
  (e: 'remove'): void;
}>();

const fileList = ref<UploadFile[]>([]);
const uploading = ref(false);
const uploadProgress = ref(0);
const error = ref('');
const uploadedFileUrl = ref('');

function beforeUpload(file: UploadFile): boolean {
  // Validate file type
  const isPDF = file.type === 'application/pdf' || file.name?.toLowerCase().endsWith('.pdf');
  if (!isPDF) {
    message.error('只能上传PDF文件');
    return false;
  }

  // Validate file size (10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size && file.size > maxSize) {
    message.error('文件大小不能超过10MB');
    return false;
  }

  // Check if file is empty
  if (file.size === 0) {
    message.error('文件不能为空');
    return false;
  }

  return true;
}

async function handleUpload(options: any) {
  const { file, onSuccess, onError, onProgress } = options;

  uploading.value = true;
  uploadProgress.value = 0;
  error.value = '';

  try {
    const formData = new FormData();
    formData.append('file', file);

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10;
        onProgress({ percent: uploadProgress.value });
      }
    }, 100);

    // Make API request
    const response = await fetch('/api/reports/upload', {
      method: 'POST',
      body: formData,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

    clearInterval(progressInterval);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '上传失败');
    }

    const data = await response.json();

    uploadProgress.value = 100;
    uploadedFileUrl.value = data.file_url;

    message.success('文件上传成功');
    onSuccess(data);
    emit('success', data);
  } catch (err: any) {
    error.value = err.message || '上传失败';
    message.error(error.value);
    onError(err);
    emit('error', err);
  } finally {
    uploading.value = false;
  }
}

function handleRemove() {
  fileList.value = [];
  uploadedFileUrl.value = '';
  uploadProgress.value = 0;
  emit('remove');
}

defineExpose({
  handleRemove,
  uploadedFileUrl,
});
</script>

<style scoped>
.report-upload {
  margin: 16px 0;
}

.upload-progress {
  margin-top: 16px;
}

.upload-error,
.uploaded-file {
  margin-top: 16px;
}
</style>
