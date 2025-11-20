<template>
  <a-modal
    :open="visible"
    title="提交检测结果"
    :confirmLoading="loading"
    @ok="handleOk"
    @cancel="handleCancel"
    width="600px"
  >
    <div v-if="checkObject" class="submit-content">
      <a-alert
        message="提交后不可撤销"
        description="请确认检测结果无误后再提交,提交后将无法修改。"
        type="warning"
        show-icon
        style="margin-bottom: 16px"
      />

      <a-descriptions title="检测信息" :column="2" bordered size="small">
        <a-descriptions-item label="检测编号">
          {{ checkObject.check_no }}
        </a-descriptions-item>
        <a-descriptions-item label="样品名称">
          {{ checkObject.sample_name }}
        </a-descriptions-item>
        <a-descriptions-item label="公司/个体">
          {{ checkObject.company_name }}
        </a-descriptions-item>
        <a-descriptions-item label="检验结果">
          <a-tag :color="checkObject.check_result === '合格' ? 'success' : 'error'">
            {{ checkObject.check_result }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="检测项目数" :span="2">
          {{ checkObject.check_items?.length || 0 }} 项
        </a-descriptions-item>
        <a-descriptions-item label="报告文件" :span="2">
          <span v-if="checkObject.report_url">
            <a :href="checkObject.report_url" target="_blank">查看报告</a>
          </span>
          <a-tag v-else color="warning">未上传报告</a-tag>
        </a-descriptions-item>
      </a-descriptions>

      <div v-if="checkObject.check_items?.length" style="margin-top: 16px">
        <h4>检测项目明细</h4>
        <a-table
          :columns="itemColumns"
          :data-source="checkObject.check_items"
          :pagination="false"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'result_indicator'">
              <a-tag
                :color="record.result_indicator === '合格' ? 'success' : 'error'"
              >
                {{ record.result_indicator || '-' }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </div>

      <div v-if="error" style="margin-top: 16px">
        <a-alert :message="error" type="error" closable @close="error = ''" />
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
/**
 * SubmitModal Component
 * T129: Confirmation dialog for submitting check results
 */
import { ref } from 'vue';
import type { CheckObjectDetail } from '@/services/checkService';

interface Props {
  visible: boolean;
  checkObject: CheckObjectDetail | null;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: 'ok'): void;
  (e: 'cancel'): void;
  (e: 'error', error: Error): void;
}>();

const error = ref('');

const itemColumns = [
  {
    title: '检测项目',
    dataIndex: 'check_item_name',
    key: 'check_item_name',
  },
  {
    title: '检测结果',
    dataIndex: 'check_result',
    key: 'check_result',
  },
  {
    title: '结果判定',
    key: 'result_indicator',
  },
];

function handleOk() {
  error.value = '';
  emit('ok');
}

function handleCancel() {
  error.value = '';
  emit('cancel');
}
</script>

<style scoped>
.submit-content h4 {
  margin-bottom: 12px;
  font-weight: 600;
}
</style>
