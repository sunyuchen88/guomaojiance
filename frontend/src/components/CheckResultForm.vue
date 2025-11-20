<template>
  <a-form
    :model="formData"
    :rules="rules"
    layout="vertical"
    @finish="handleSubmit"
  >
    <a-form-item label="检验结果" name="check_result" required>
      <a-select
        v-model:value="formData.check_result"
        placeholder="请选择检验结果"
        size="large"
      >
        <a-select-option value="合格">合格</a-select-option>
        <a-select-option value="不合格">不合格</a-select-option>
        <a-select-option value="基本合格">基本合格</a-select-option>
      </a-select>
    </a-form-item>

    <a-divider>检测项目结果</a-divider>

    <a-table
      :columns="columns"
      :data-source="checkItems"
      :pagination="false"
      row-key="id"
      size="small"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === 'check_result'">
          <a-input
            v-model:value="itemResults[index].check_result"
            placeholder="请输入检测结果"
          />
        </template>
        <template v-else-if="column.key === 'result_indicator'">
          <a-select
            v-model:value="itemResults[index].result_indicator"
            placeholder="结果判定"
            style="width: 100%"
          >
            <a-select-option value="合格">合格</a-select-option>
            <a-select-option value="不合格">不合格</a-select-option>
            <a-select-option value="基本合格">基本合格</a-select-option>
          </a-select>
        </template>
      </template>
    </a-table>

    <a-form-item style="margin-top: 24px">
      <a-space>
        <a-button type="primary" html-type="submit" :loading="loading">
          保存结果
        </a-button>
        <a-button @click="handleReset">
          重置
        </a-button>
      </a-space>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
/**
 * CheckResultForm Component
 * T113: Form for inputting check results
 */
import { ref, reactive, watch } from 'vue';

interface CheckItem {
  id: number;
  check_item_name: string;
  check_method: string;
  standard_value?: string;
}

interface ItemResult {
  id: number;
  check_result: string;
  result_indicator: string;
}

interface Props {
  checkItems: CheckItem[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: 'submit', data: { check_result: string; check_items: ItemResult[] }): void;
  (e: 'reset'): void;
}>();

const formData = reactive({
  check_result: '',
});

const itemResults = ref<ItemResult[]>([]);

// Initialize item results
watch(
  () => props.checkItems,
  (items) => {
    itemResults.value = items.map((item) => ({
      id: item.id,
      check_result: '',
      result_indicator: '',
    }));
  },
  { immediate: true }
);

const rules = {
  check_result: [
    { required: true, message: '请选择检验结果', trigger: 'change' },
  ],
};

const columns = [
  {
    title: '检测项目',
    dataIndex: 'check_item_name',
    key: 'check_item_name',
    width: 150,
  },
  {
    title: '检测方法',
    dataIndex: 'check_method',
    key: 'check_method',
    width: 150,
  },
  {
    title: '标准值',
    dataIndex: 'standard_value',
    key: 'standard_value',
    width: 120,
  },
  {
    title: '检测结果',
    key: 'check_result',
    width: 180,
  },
  {
    title: '结果判定',
    key: 'result_indicator',
    width: 120,
  },
];

function handleSubmit() {
  const data = {
    check_result: formData.check_result,
    check_items: itemResults.value.filter(
      (item) => item.check_result || item.result_indicator
    ),
  };

  emit('submit', data);
}

function handleReset() {
  formData.check_result = '';
  itemResults.value = props.checkItems.map((item) => ({
    id: item.id,
    check_result: '',
    result_indicator: '',
  }));
  emit('reset');
}
</script>

<style scoped>
:deep(.ant-table-small .ant-table-cell) {
  padding: 8px;
}
</style>
