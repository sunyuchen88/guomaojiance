<template>
  <a-form layout="inline" class="query-filter">
    <a-form-item label="状态">
      <a-select
        v-model:value="filters.status"
        placeholder="全部状态"
        style="width: 120px"
        allowClear
        @change="handleSearch"
      >
        <a-select-option :value="0">待检测</a-select-option>
        <a-select-option :value="1">已检测</a-select-option>
        <a-select-option :value="2">提交成功</a-select-option>
        <a-select-option :value="3">提交失败</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item label="公司名称">
      <a-input
        v-model:value="filters.company"
        placeholder="请输入公司名称"
        style="width: 160px"
        allowClear
        @pressEnter="handleSearch"
      />
    </a-form-item>

    <a-form-item label="检测编号">
      <a-input
        v-model:value="filters.checkNo"
        placeholder="请输入检测编号"
        style="width: 160px"
        allowClear
        @pressEnter="handleSearch"
      />
    </a-form-item>

    <a-form-item label="采样时间">
      <a-range-picker
        v-model:value="dateRange"
        format="YYYY-MM-DD"
        :placeholder="['开始日期', '结束日期']"
        style="width: 240px"
        @change="handleDateChange"
      />
    </a-form-item>

    <a-form-item label="检测结果">
      <a-select
        v-model:value="filters.checkResult"
        placeholder="全部结果"
        style="width: 120px"
        allowClear
        @change="handleSearch"
      >
        <a-select-option value="合格">合格</a-select-option>
        <a-select-option value="不合格">不合格</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item>
      <a-space>
        <a-button type="primary" @click="handleSearch">
          <template #icon>
            <SearchOutlined />
          </template>
          查询
        </a-button>
        <a-button @click="handleReset">
          <template #icon>
            <ReloadOutlined />
          </template>
          重置
        </a-button>
      </a-space>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
/**
 * QueryFilter Component
 * T094: Status, company, check_no, date range filters
 */
import { reactive, ref, watch } from 'vue';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import type { Dayjs } from 'dayjs';

export interface FilterValues {
  status: number | null;
  company: string;
  checkNo: string;
  startDate: string | null;
  endDate: string | null;
  checkResult: string | null;  // 需求2.3: 检测结果筛选
}

interface Props {
  modelValue?: FilterValues;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({
    status: null,
    company: '',
    checkNo: '',
    startDate: null,
    endDate: null,
    checkResult: null,
  }),
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: FilterValues): void;
  (e: 'search', filters: FilterValues): void;
  (e: 'reset'): void;
}>();

const filters = reactive<FilterValues>({
  status: props.modelValue.status,
  company: props.modelValue.company,
  checkNo: props.modelValue.checkNo,
  startDate: props.modelValue.startDate,
  endDate: props.modelValue.endDate,
  checkResult: props.modelValue.checkResult,
});

const dateRange = ref<[Dayjs, Dayjs] | null>(null);

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    filters.status = newValue.status;
    filters.company = newValue.company;
    filters.checkNo = newValue.checkNo;
    filters.startDate = newValue.startDate;
    filters.endDate = newValue.endDate;
    filters.checkResult = newValue.checkResult;
  },
  { deep: true }
);

function handleDateChange(dates: [Dayjs, Dayjs] | null) {
  if (dates) {
    filters.startDate = dates[0].format('YYYY-MM-DD');
    filters.endDate = dates[1].format('YYYY-MM-DD');
  } else {
    filters.startDate = null;
    filters.endDate = null;
  }
}

function handleSearch() {
  emit('update:modelValue', { ...filters });
  emit('search', { ...filters });
}

function handleReset() {
  filters.status = null;
  filters.company = '';
  filters.checkNo = '';
  filters.startDate = null;
  filters.endDate = null;
  filters.checkResult = null;
  dateRange.value = null;

  emit('update:modelValue', { ...filters });
  emit('reset');
}
</script>

<style scoped>
.query-filter {
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
}

.query-filter :deep(.ant-form-item) {
  margin-bottom: 8px;
}
</style>
