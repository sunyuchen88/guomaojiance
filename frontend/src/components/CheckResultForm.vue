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

    <a-divider>检测项目结果 (T2.2: 5个核心字段)</a-divider>

    <a-space direction="vertical" style="width: 100%">
      <a-button type="dashed" block @click="handleAddItem">
        <template #icon><PlusOutlined /></template>
        添加检测项目
      </a-button>

      <a-table
        :columns="columns"
        :data-source="itemResults"
        :pagination="false"
        row-key="key"
        size="small"
        bordered
      >
        <template #bodyCell="{ column, record, index }">
          <template v-if="column.key === 'check_item_name'">
            <a-input
              v-model:value="itemResults[index].check_item_name"
              placeholder="检测项目名称"
            />
          </template>
          <template v-else-if="column.key === 'check_method'">
            <a-input
              v-model:value="itemResults[index].check_method"
              placeholder="检测方法"
            />
          </template>
          <template v-else-if="column.key === 'unit'">
            <a-input
              v-model:value="itemResults[index].unit"
              placeholder="单位"
              style="width: 80px"
            />
          </template>
          <template v-else-if="column.key === 'num'">
            <a-input
              v-model:value="itemResults[index].num"
              placeholder="检测结果"
            />
          </template>
          <template v-else-if="column.key === 'detection_limit'">
            <a-input
              v-model:value="itemResults[index].detection_limit"
              placeholder="检出限"
            />
          </template>
          <template v-else-if="column.key === 'result'">
            <a-select
              v-model:value="itemResults[index].result"
              placeholder="结果判定"
              style="width: 100%"
            >
              <a-select-option value="合格">合格</a-select-option>
              <a-select-option value="不合格">不合格</a-select-option>
              <a-select-option value="基本合格">基本合格</a-select-option>
            </a-select>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-button
              type="link"
              danger
              size="small"
              @click="handleRemoveItem(index)"
            >
              删除
            </a-button>
          </template>
        </template>
      </a-table>
    </a-space>

    <a-divider />

    <a-form-item label="上传检测报告" name="report_file">
      <a-upload
        v-model:file-list="fileList"
        :before-upload="beforeUpload"
        accept=".pdf"
        :max-count="1"
      >
        <a-button>
          <template #icon><UploadOutlined /></template>
          选择PDF文件
        </a-button>
      </a-upload>
      <div style="margin-top: 8px; color: #999; font-size: 12px">
        仅支持PDF格式，文件大小不超过10MB
      </div>
    </a-form-item>

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
 * T113, T2.2: Form for inputting check results with 5 core fields
 * - 检测项目 (check_item_name)
 * - 检测方法 (check_method)
 * - 单位 (unit)
 * - 检测结果 (num)
 * - 检出限 (detection_limit)
 * Support adding multiple rows dynamically
 */
import { ref, reactive, watch } from 'vue';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

interface CheckItem {
  id: number;
  check_item_name: string;
  check_method?: string;
  unit?: string;
  num?: string;
  detection_limit?: string;
  result?: string;
}

interface ItemResult {
  key: number;
  id?: number;
  check_item_name: string;
  check_method: string;
  unit: string;
  num: string;
  detection_limit: string;
  result: string;
}

interface Props {
  checkItems: CheckItem[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: 'submit', data: {
    check_result: string;
    check_items: ItemResult[];
    report_file?: File;
  }): void;
  (e: 'reset'): void;
}>();

const formData = reactive({
  check_result: '',
});

const itemResults = ref<ItemResult[]>([]);
const fileList = ref<any[]>([]);
let nextKey = 1;

// Initialize item results from existing check items
watch(
  () => props.checkItems,
  (items) => {
    if (items && items.length > 0) {
      itemResults.value = items.map((item) => ({
        key: nextKey++,
        id: item.id,
        check_item_name: item.check_item_name || '',
        check_method: item.check_method || '',
        unit: item.unit || '',
        num: item.num || '',
        detection_limit: item.detection_limit || '',
        result: item.result || '',
      }));
    }
  },
  { immediate: true }
);

const rules = {
  check_result: [
    { required: true, message: '请选择检验结果', trigger: 'change' },
  ],
};

// T2.2: 5个核心字段 + 结果判定 + 操作列
const columns = [
  {
    title: '检测项目',
    key: 'check_item_name',
    width: 150,
  },
  {
    title: '检测方法',
    key: 'check_method',
    width: 150,
  },
  {
    title: '单位',
    key: 'unit',
    width: 100,
  },
  {
    title: '检测结果',
    key: 'num',
    width: 120,
  },
  {
    title: '检出限',
    key: 'detection_limit',
    width: 120,
  },
  {
    title: '结果判定',
    key: 'result',
    width: 120,
  },
  {
    title: '操作',
    key: 'actions',
    width: 80,
    fixed: 'right',
  },
];

// T2.2: Support adding multiple rows
function handleAddItem() {
  itemResults.value.push({
    key: nextKey++,
    check_item_name: '',
    check_method: '',
    unit: '',
    num: '',
    detection_limit: '',
    result: '',
  });
}

function handleRemoveItem(index: number) {
  itemResults.value.splice(index, 1);
}

// File upload validation
const beforeUpload = (file: File) => {
  const isPDF = file.type === 'application/pdf';
  if (!isPDF) {
    message.error('只能上传PDF文件!');
    return false;
  }
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    message.error('文件大小不能超过10MB!');
    return false;
  }
  return false; // Prevent auto upload
};

function handleSubmit() {
  // Validate at least one item has data
  const validItems = itemResults.value.filter(
    (item) => item.check_item_name || item.num
  );

  if (validItems.length === 0) {
    message.warning('请至少填写一个检测项目');
    return;
  }

  const data: any = {
    check_result: formData.check_result,
    check_items: validItems,
  };

  // Add report file if selected
  if (fileList.value.length > 0) {
    const file = fileList.value[0].originFileObj || fileList.value[0];
    data.report_file = file;
  }

  emit('submit', data);
}

function handleReset() {
  formData.check_result = '';
  itemResults.value = props.checkItems.map((item) => ({
    key: nextKey++,
    id: item.id,
    check_item_name: item.check_item_name || '',
    check_method: item.check_method || '',
    unit: item.unit || '',
    num: item.num || '',
    detection_limit: item.detection_limit || '',
    result: item.result || '',
  }));
  fileList.value = [];
  emit('reset');
}
</script>

<style scoped>
:deep(.ant-table-small .ant-table-cell) {
  padding: 8px 4px;
}

:deep(.ant-input),
:deep(.ant-select) {
  font-size: 13px;
}
</style>
