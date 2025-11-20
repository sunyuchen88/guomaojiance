<template>
  <div class="check-detail-container">
    <a-page-header
      title="检测详情"
      @back="handleBack"
    >
      <template #extra>
        <a-space>
          <a-button @click="handleBack">返回列表</a-button>
          <a-button
            v-if="checkObject && checkObject.status === 0"
            type="primary"
            @click="showResultModal"
          >
            录入检测结果
          </a-button>
          <a-button
            v-if="checkObject && checkObject.status === 1"
            type="primary"
            danger
            @click="showSubmitModal"
          >
            提交检测结果
          </a-button>
          <a-button type="primary" @click="handleSave" :loading="saving">
            保存修改
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-spin :spinning="loading">
      <a-card v-if="checkObject" title="样品基本信息">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="检测编号">
            {{ checkObject.check_no }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(checkObject.status)">
              {{ getStatusText(checkObject.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="样品名称">
            <a-input
              v-model:value="editForm.sample_name"
              placeholder="请输入样品名称"
            />
          </a-descriptions-item>
          <a-descriptions-item label="公司/个体">
            <a-input
              v-model:value="editForm.company_name"
              placeholder="请输入公司名称"
            />
          </a-descriptions-item>
          <a-descriptions-item label="样品来源">
            {{ checkObject.sample_source || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="规格型号">
            {{ checkObject.specs || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="采样时间">
            {{ formatDate(checkObject.sampling_time) }}
          </a-descriptions-item>
          <a-descriptions-item label="采样地点">
            {{ checkObject.sampling_site || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="委托单位" :span="2">
            {{ checkObject.commissioning_unit || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="检验结果">
            {{ checkObject.check_result || '待检测' }}
          </a-descriptions-item>
          <a-descriptions-item label="报告链接">
            <a v-if="checkObject.report_url" :href="checkObject.report_url" target="_blank">
              查看报告
            </a>
            <span v-else>-</span>
          </a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">
            <a-textarea
              v-model:value="editForm.remark"
              placeholder="请输入备注"
              :rows="2"
            />
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <a-card v-if="checkObject" title="检测项目" style="margin-top: 16px">
        <a-table
          :columns="itemColumns"
          :data-source="checkObject.check_items"
          :pagination="false"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'check_result'">
              {{ record.check_result || '-' }}
            </template>
            <template v-else-if="column.key === 'result_indicator'">
              <a-tag v-if="record.result_indicator" :color="record.result_indicator === '合格' ? 'success' : 'error'">
                {{ record.result_indicator }}
              </a-tag>
              <span v-else>-</span>
            </template>
          </template>
        </a-table>
      </a-card>
    </a-spin>

    <!-- Result Input Modal (T115) -->
    <a-modal
      v-model:open="resultModalVisible"
      title="录入检测结果"
      width="800px"
      :footer="null"
      :maskClosable="false"
    >
      <CheckResultForm
        v-if="checkObject"
        :check-items="checkObject.check_items"
        :loading="submittingResult"
        @submit="handleSubmitResult"
        @reset="handleResetResult"
      />
    </a-modal>

    <!-- Report Upload Modal -->
    <a-modal
      v-model:open="uploadModalVisible"
      title="上传检测报告"
      width="600px"
      :footer="null"
    >
      <ReportUpload
        @success="handleUploadSuccess"
        @error="handleUploadError"
      />
    </a-modal>

    <!-- Submit Confirmation Modal (T130) -->
    <SubmitModal
      :visible="submitModalVisible"
      :check-object="checkObject"
      :loading="submitting"
      @ok="handleSubmitConfirm"
      @cancel="submitModalVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * CheckDetailView - View and edit check object details
 * T097, T115, T119, T130, T132: Edit, result input, submit, notifications
 */
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  getCheckObjectDetail,
  updateCheckObject,
  saveCheckResult,
  submitResult,
  uploadReport,
  getStatusText,
  getStatusColor,
  type CheckObjectDetail,
} from '@/services/checkService';
import CheckResultForm from '@/components/CheckResultForm.vue';
import ReportUpload from '@/components/ReportUpload.vue';
import SubmitModal from '@/components/SubmitModal.vue';
import dayjs from 'dayjs';

const router = useRouter();
const route = useRoute();

const loading = ref(false);
const saving = ref(false);
const submittingResult = ref(false);
const submitting = ref(false);
const resultModalVisible = ref(false);
const uploadModalVisible = ref(false);
const submitModalVisible = ref(false);
const checkObject = ref<CheckObjectDetail | null>(null);

const editForm = reactive({
  sample_name: '',
  company_name: '',
  remark: '',
});

const itemColumns = [
  {
    title: '检测项目',
    dataIndex: 'check_item_name',
    key: 'check_item_name',
  },
  {
    title: '检测方法',
    dataIndex: 'check_method',
    key: 'check_method',
  },
  {
    title: '标准值',
    dataIndex: 'standard_value',
    key: 'standard_value',
  },
  {
    title: '检测结果',
    key: 'check_result',
    dataIndex: 'check_result',
  },
  {
    title: '结果判定',
    key: 'result_indicator',
    dataIndex: 'result_indicator',
  },
];

onMounted(() => {
  loadDetail();
});

async function loadDetail() {
  const id = Number(route.params.id);
  if (!id) {
    message.error('无效的检测对象ID');
    router.push('/');
    return;
  }

  loading.value = true;

  try {
    const data = await getCheckObjectDetail(id);
    checkObject.value = data;

    // Initialize edit form
    editForm.sample_name = data.sample_name || '';
    editForm.company_name = data.company_name || '';
    editForm.remark = data.remark || '';
  } catch (error: any) {
    message.error('加载详情失败');
    router.push('/');
  } finally {
    loading.value = false;
  }
}

async function handleSave() {
  if (!checkObject.value) return;

  saving.value = true;

  try {
    await updateCheckObject(checkObject.value.id, {
      sample_name: editForm.sample_name,
      company_name: editForm.company_name,
      remark: editForm.remark,
    });

    // T119: Add success notification
    message.success('保存成功');
    loadDetail();
  } catch (error: any) {
    message.error('保存失败');
  } finally {
    saving.value = false;
  }
}

function showResultModal() {
  resultModalVisible.value = true;
}

async function handleSubmitResult(data: {
  check_result: string;
  check_items: Array<{
    id?: number;
    check_item_name: string;
    check_method: string;
    unit: string;
    num: string;
    detection_limit: string;
    result: string;
  }>;
  report_file?: File;
}) {
  if (!checkObject.value) return;

  submittingResult.value = true;

  try {
    // T2.2: First upload report if provided
    let reportUrl = checkObject.value.report_url;
    if (data.report_file) {
      try {
        const uploadResult = await uploadReport(data.report_file);
        reportUrl = uploadResult.file_url;
        message.success('报告上传成功');
      } catch (error: any) {
        message.error('报告上传失败: ' + (error.response?.data?.detail || error.message));
        return;
      }
    }

    // Then save check results
    await saveCheckResult(checkObject.value.id, {
      check_result: data.check_result,
      check_items: data.check_items,
    });

    // T119: Add success notification
    message.success('检测结果保存成功');
    resultModalVisible.value = false;
    loadDetail();
  } catch (error: any) {
    message.error('保存失败: ' + (error.response?.data?.detail || error.message));
  } finally {
    submittingResult.value = false;
  }
}

function handleResetResult() {
  // Reset is handled in CheckResultForm
}

function showUploadModal() {
  uploadModalVisible.value = true;
}

function handleUploadSuccess(data: { file_url: string; filename: string }) {
  // T119: Add success notification
  message.success('报告上传成功');
  uploadModalVisible.value = false;

  // Update report URL
  if (checkObject.value) {
    checkObject.value.report_url = data.file_url;
  }
}

function handleUploadError(error: Error) {
  message.error('上传失败: ' + error.message);
}

function showSubmitModal() {
  submitModalVisible.value = true;
}

async function handleSubmitConfirm() {
  if (!checkObject.value) return;

  submitting.value = true;

  try {
    // T131, T132: Submit result and handle success/failure
    await submitResult(checkObject.value.id);

    // T132: Success handling
    message.success('提交成功');
    submitModalVisible.value = false;
    loadDetail();
  } catch (error: any) {
    // T132: Failure handling with error details
    const errorMessage = error.response?.data?.detail || error.message || '提交失败';
    message.error(errorMessage);
  } finally {
    submitting.value = false;
  }
}

function handleBack() {
  router.push('/');
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm');
}
</script>

<style scoped>
.check-detail-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

.check-detail-container :deep(.ant-page-header) {
  background: #fff;
  margin-bottom: 16px;
}
</style>
