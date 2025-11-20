<template>
  <div class="report-manage-container">
    <a-card title="报告管理" :bordered="false">
      <!-- 操作按钮区域 -->
      <a-space style="margin-bottom: 16px">
        <a-button type="primary" @click="showUploadModal">
          <template #icon><UploadOutlined /></template>
          上传报告
        </a-button>
        <a-button @click="showExportModal">
          <template #icon><ExportOutlined /></template>
          导出Excel
        </a-button>
      </a-space>

      <!-- 搜索过滤区域 -->
      <a-form layout="inline" style="margin-bottom: 16px">
        <a-form-item label="检测编号">
          <a-input
            v-model:value="searchForm.check_no"
            placeholder="请输入检测编号"
            style="width: 200px"
            @pressEnter="handleSearch"
          />
        </a-form-item>
        <a-form-item label="送检公司">
          <a-input
            v-model:value="searchForm.company"
            placeholder="请输入公司名称"
            style="width: 200px"
            @pressEnter="handleSearch"
          />
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model:value="searchForm.status"
            placeholder="请选择状态"
            style="width: 120px"
            allowClear
          >
            <a-select-option :value="0">待检测</a-select-option>
            <a-select-option :value="1">已检测</a-select-option>
            <a-select-option :value="2">已提交</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </a-space>
        </a-form-item>
      </a-form>

      <!-- 数据表格 -->
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'check_result_url'">
            <a-space v-if="record.check_result_url">
              <a-button
                type="link"
                size="small"
                @click="handleDownloadReport(record)"
              >
                <template #icon><DownloadOutlined /></template>
                下载
              </a-button>
            </a-space>
            <span v-else style="color: #999">暂无报告</span>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="handleViewDetail(record)"
              >
                查看
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 上传报告模态框 -->
    <a-modal
      v-model:open="uploadModalVisible"
      title="上传报告"
      @ok="handleUploadOk"
      @cancel="handleUploadCancel"
    >
      <a-form :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="选择文件" required>
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
      </a-form>
    </a-modal>

    <!-- 导出Excel模态框 -->
    <a-modal
      v-model:open="exportModalVisible"
      title="导出Excel"
      @ok="handleExportOk"
      @cancel="handleExportCancel"
    >
      <a-form :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="导出范围">
          <a-radio-group v-model:value="exportType">
            <a-radio value="selected">导出选中项</a-radio>
            <a-radio value="filtered">导出当前筛选结果</a-radio>
            <a-radio value="all">导出全部</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-alert
          v-if="exportType === 'selected' && selectedRowKeys.length === 0"
          message="请先在列表中选择要导出的数据"
          type="warning"
          show-icon
          style="margin-bottom: 16px"
        />
        <a-alert
          message="注意：单次导出数据不能超过1000行"
          type="info"
          show-icon
        />
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  UploadOutlined,
  ExportOutlined,
  DownloadOutlined,
} from '@ant-design/icons-vue';
import type { TableColumnsType, TablePaginationConfig } from 'ant-design-vue';
import {
  getCheckObjects,
  uploadReport,
  downloadReport,
  exportExcel,
  type CheckObjectList,
} from '@/services/checkService';

// Helper function to trigger file download
const triggerDownload = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

interface CheckObject {
  id: number;
  check_object_union_num: string;
  submission_goods_name: string;
  submission_person_company: string;
  status: number;
  check_start_time: string;
  check_result: string;
  check_result_url: string;
}

// 搜索表单
const searchForm = reactive({
  check_no: '',
  company: '',
  status: undefined as number | undefined,
});

// 表格数据
const dataSource = ref<CheckObject[]>([]);
const loading = ref(false);
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
});

// 选中的行
const selectedRowKeys = ref<number[]>([]);
const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
  },
};

// 上传模态框
const uploadModalVisible = ref(false);
const fileList = ref<any[]>([]);
const uploadLoading = ref(false);

// 导出模态框
const exportModalVisible = ref(false);
const exportType = ref<'selected' | 'filtered' | 'all'>('selected');
const exportLoading = ref(false);

// 表格列定义
const columns: TableColumnsType = [
  {
    title: '检测编号',
    dataIndex: 'check_object_union_num',
    key: 'check_object_union_num',
    width: 150,
  },
  {
    title: '样品名称',
    dataIndex: 'submission_goods_name',
    key: 'submission_goods_name',
    width: 150,
  },
  {
    title: '送检公司',
    dataIndex: 'submission_person_company',
    key: 'submission_person_company',
    width: 200,
  },
  {
    title: '状态',
    key: 'status',
    dataIndex: 'status',
    width: 100,
  },
  {
    title: '检测时间',
    dataIndex: 'check_start_time',
    key: 'check_start_time',
    width: 180,
  },
  {
    title: '检测结果',
    dataIndex: 'check_result',
    key: 'check_result',
    width: 100,
  },
  {
    title: '报告文件',
    key: 'check_result_url',
    width: 120,
  },
  {
    title: '操作',
    key: 'action',
    width: 100,
    fixed: 'right',
  },
];

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.current,
      page_size: pagination.pageSize,
    };

    if (searchForm.check_no) {
      params.check_no = searchForm.check_no;
    }
    if (searchForm.company) {
      params.company = searchForm.company;
    }
    if (searchForm.status !== undefined) {
      params.status = searchForm.status;
    }

    const response = await getCheckObjects(params);
    dataSource.value = response.items;
    pagination.total = response.total;
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.current = 1;
  loadData();
};

// 重置
const handleReset = () => {
  searchForm.check_no = '';
  searchForm.company = '';
  searchForm.status = undefined;
  pagination.current = 1;
  loadData();
};

// 表格变化
const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.current = pag.current || 1;
  pagination.pageSize = pag.pageSize || 10;
  loadData();
};

// 状态颜色
const getStatusColor = (status: number) => {
  const colors: Record<number, string> = {
    0: 'blue',
    1: 'green',
    2: 'orange',
  };
  return colors[status] || 'default';
};

// 状态文本
const getStatusText = (status: number) => {
  const texts: Record<number, string> = {
    0: '待检测',
    1: '已检测',
    2: '已提交',
  };
  return texts[status] || '未知';
};

// 显示上传模态框
const showUploadModal = () => {
  uploadModalVisible.value = true;
  fileList.value = [];
};

// 文件上传前验证
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
  return false; // 阻止自动上传
};

// 上传确认
const handleUploadOk = async () => {
  if (fileList.value.length === 0) {
    message.warning('请选择要上传的文件');
    return;
  }

  uploadLoading.value = true;
  try {
    const file = fileList.value[0].originFileObj || fileList.value[0];
    const result = await uploadReport(file);
    message.success('报告上传成功');
    uploadModalVisible.value = false;
    fileList.value = [];
    loadData(); // 重新加载数据
  } catch (error: any) {
    message.error(error.response?.data?.detail || '上传失败');
  } finally {
    uploadLoading.value = false;
  }
};

// 上传取消
const handleUploadCancel = () => {
  uploadModalVisible.value = false;
  fileList.value = [];
};

// 下载报告
const handleDownloadReport = async (record: CheckObject) => {
  try {
    message.loading({ content: '正在下载...', key: 'download' });
    const blob = await downloadReport(record.check_object_union_num);
    triggerDownload(blob, `${record.check_object_union_num}_report.pdf`);
    message.success({ content: '下载成功', key: 'download' });
  } catch (error: any) {
    message.error({
      content: error.response?.data?.detail || '下载失败',
      key: 'download',
    });
  }
};

// 显示导出模态框
const showExportModal = () => {
  exportModalVisible.value = true;
  exportType.value = selectedRowKeys.value.length > 0 ? 'selected' : 'filtered';
};

// 导出确认
const handleExportOk = async () => {
  if (exportType.value === 'selected' && selectedRowKeys.value.length === 0) {
    message.warning('请先选择要导出的数据');
    return;
  }

  exportLoading.value = true;
  try {
    message.loading({ content: '正在导出...', key: 'export' });

    let request: any = {};

    if (exportType.value === 'selected') {
      request.check_object_ids = selectedRowKeys.value;
    } else if (exportType.value === 'filtered') {
      // 使用当前筛选条件
      if (searchForm.check_no) request.check_no = searchForm.check_no;
      if (searchForm.company) request.company = searchForm.company;
      if (searchForm.status !== undefined) request.status = searchForm.status;
    }
    // exportType === 'all' 时不传任何参数

    const blob = await exportExcel(request);
    const filename = `检测报告_${new Date().toISOString().slice(0, 10)}.xlsx`;
    triggerDownload(blob, filename);

    message.success({ content: '导出成功', key: 'export' });
    exportModalVisible.value = false;
  } catch (error: any) {
    message.error({
      content: error.response?.data?.detail || '导出失败',
      key: 'export',
    });
  } finally {
    exportLoading.value = false;
  }
};

// 导出取消
const handleExportCancel = () => {
  exportModalVisible.value = false;
};

// 查看详情
const handleViewDetail = (record: CheckObject) => {
  // TODO: 跳转到详情页面或打开详情模态框
  message.info('查看详情功能开发中');
};

// 初始化
onMounted(() => {
  loadData();
});
</script>

<style scoped>
.report-manage-container {
  padding: 24px;
}

:deep(.ant-table) {
  font-size: 14px;
}

:deep(.ant-pagination) {
  margin-top: 16px;
}
</style>
