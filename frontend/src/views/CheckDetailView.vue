<template>
  <div class="check-detail-container">
    <a-page-header
      title="检测详情"
      @back="handleBack"
    >
      <template #extra>
        <a-space>
          <a-button @click="handleBack">返回列表</a-button>
          <a-button type="primary" @click="handleSave" :loading="saving">
            保存修改
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-spin :spinning="loading">
      <a-card v-if="checkObject" title="样品基本信息">
        <a-descriptions :column="2" bordered>
          <!-- 需求2.5.1: 第1行 -->
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

          <!-- 需求2.5.1: 第2行 -->
          <a-descriptions-item label="样品编号">
            <a-input
              v-model:value="editForm.check_object_union_num"
              placeholder="请输入样品编号"
            />
          </a-descriptions-item>
          <a-descriptions-item label="委托单位名称">
            <a-input
              v-model:value="editForm.company_name"
              placeholder="请输入委托单位名称"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第3行 -->
          <a-descriptions-item label="委托单位地址" :span="2">
            <a-input
              v-model:value="editForm.commission_unit_address"
              placeholder="请输入委托单位地址"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第4行 -->
          <a-descriptions-item label="生产日期">
            <a-date-picker
              v-model:value="editForm.production_date"
              placeholder="请选择生产日期"
              style="width: 100%"
              format="YYYY-MM-DD"
              :allow-clear="true"
            />
          </a-descriptions-item>
          <a-descriptions-item label="样品数量">
            <a-input
              v-model:value="editForm.sample_quantity"
              placeholder="请输入样品数量"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第5行 -->
          <a-descriptions-item label="样品类别">
            <a-input
              v-model:value="editForm.check_type"
              placeholder="请输入样品类别"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第6行 -->
          <a-descriptions-item label="联系人">
            <a-input
              v-model:value="editForm.submission_person"
              placeholder="请输入联系人"
            />
          </a-descriptions-item>
          <a-descriptions-item label="联系电话">
            <a-input
              v-model:value="editForm.submission_person_mobile"
              placeholder="请输入联系电话"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第7行 -->
          <a-descriptions-item label="收样日期">
            <a-date-picker
              v-model:value="editForm.create_time"
              placeholder="请选择收样日期"
              style="width: 100%"
              format="YYYY-MM-DD HH:mm"
              show-time
              :allow-clear="true"
            />
          </a-descriptions-item>
          <a-descriptions-item label="检测日期">
            <a-date-picker
              v-model:value="editForm.inspection_date"
              placeholder="请选择检测日期"
              style="width: 100%"
              format="YYYY-MM-DD"
              :allow-clear="true"
            />
          </a-descriptions-item>

          <!-- 需求2.5.1: 第8行 -->
          <a-descriptions-item label="车牌号">
            <a-input
              v-model:value="editForm.submission_goods_car_number"
              placeholder="请输入车牌号"
            />
          </a-descriptions-item>
          <a-descriptions-item label="备注">
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
          :data-source="editForm.check_items"
          :pagination="false"
          row-key="id"
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'check_item_id'">
              {{ record.check_item_id || '-' }}
            </template>
            <template v-else-if="column.key === 'check_item_name'">
              <a-input
                v-model:value="editForm.check_items[index].check_item_name"
                placeholder="检验项目"
              />
            </template>
            <template v-else-if="column.key === 'unit'">
              <a-input
                v-model:value="editForm.check_items[index].unit"
                placeholder="单位"
              />
            </template>
            <template v-else-if="column.key === 'num'">
              <a-input
                v-model:value="editForm.check_items[index].num"
                placeholder="检测结果"
              />
            </template>
            <template v-else-if="column.key === 'detection_limit'">
              <a-input
                v-model:value="editForm.check_items[index].detection_limit"
                placeholder="检出限"
              />
            </template>
            <template v-else-if="column.key === 'check_method'">
              <a-input
                v-model:value="editForm.check_items[index].check_method"
                placeholder="检测方法"
              />
            </template>
          </template>
        </a-table>
      </a-card>

      <!-- 需求2.5.3: 总体检测结果 + 上传检测报告 -->
      <a-card v-if="checkObject" title="检测结果" style="margin-top: 16px">
        <a-form layout="vertical">
          <a-form-item label="总体检测结果">
            <a-select
              v-model:value="editForm.check_result"
              placeholder="请选择检测结果"
              style="width: 200px"
            >
              <a-select-option value="合格">合格</a-select-option>
              <a-select-option value="不合格">不合格</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="上传检测报告">
            <a-upload
              v-model:file-list="reportFileList"
              :before-upload="beforeUploadReport"
              accept=".pdf"
              :max-count="1"
            >
              <a-button>
                <UploadOutlined />
                {{ uploadedReportName ? '重新上传PDF文件' : '选择PDF文件' }}
              </a-button>
            </a-upload>

            <!-- 显示已上传的报告 -->
            <div v-if="uploadedReportName" style="margin-top: 8px">
              <span style="color: #52c41a; margin-right: 8px">✓ 已上传：</span>
              <a
                @click="handleDownloadReport"
                style="cursor: pointer; color: #1890ff; text-decoration: underline;"
              >
                {{ uploadedReportName }}
              </a>
            </div>

            <div style="margin-top: 8px; color: #999; font-size: 12px">
              仅支持PDF格式，文件大小不超过10MB。重新上传将覆盖原有报告。
            </div>
          </a-form-item>
        </a-form>
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
import { UploadOutlined } from '@ant-design/icons-vue';
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
const reportFileList = ref<any[]>([]); // 需求2.5.3: 报告文件列表
const uploadedReportName = ref<string>(''); // 已上传的报告名称

const editForm = reactive({
  sample_name: '',
  company_name: '',
  remark: '',
  // 需求: 所有样品基本信息字段都可编辑
  check_object_union_num: '',
  check_type: '',
  submission_person: '',
  submission_person_mobile: '',
  submission_goods_car_number: '',
  create_time: null as any,
  // 需求2.5.1: 新增字段
  commission_unit_address: '',
  production_date: null as any,
  sample_quantity: '',
  inspection_date: null as any,
  // 需求2.5.2: 检测项目（可编辑）
  check_items: [] as any[],
  // 需求2.5.3: 总体检测结果和报告
  check_result: '',
  report_file: null as File | null,
  report_url: '', // 当前报告URL
});

// 需求2.5.2: 检测项目表格列定义
const itemColumns = [
  {
    title: '序号',
    dataIndex: 'check_item_id',
    key: 'check_item_id',
    width: 80,
  },
  {
    title: '检验项目',
    dataIndex: 'check_item_name',
    key: 'check_item_name',
    width: 150,
  },
  {
    title: '单位',
    dataIndex: 'unit',
    key: 'unit',
    width: 100,
  },
  {
    title: '检测结果',
    key: 'num',
    dataIndex: 'num',
    width: 120,
  },
  {
    title: '检出限',
    key: 'detection_limit',
    dataIndex: 'detection_limit',
    width: 100,
  },
  {
    title: '检测方法',
    dataIndex: 'check_method',
    key: 'check_method',
    width: 150,
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
    // 所有样品基本信息字段都可编辑
    editForm.check_object_union_num = data.check_object_union_num || '';
    editForm.check_type = data.check_type || '';
    editForm.submission_person = data.submission_person || '';
    editForm.submission_person_mobile = data.submission_person_mobile || '';
    editForm.submission_goods_car_number = data.submission_goods_car_number || '';
    // 日期字段转换为dayjs对象
    editForm.create_time = data.create_time ? dayjs(data.create_time) : null;
    // 需求2.5.1: 初始化新字段
    editForm.commission_unit_address = data.commission_unit_address || '';
    editForm.production_date = data.production_date && data.production_date !== '/' ? dayjs(data.production_date) : null;
    editForm.sample_quantity = data.sample_quantity || '';
    editForm.inspection_date = data.inspection_date ? dayjs(data.inspection_date) : null;
    // 需求2.5.2: 初始化检测项目（可编辑）
    editForm.check_items = data.check_items ? JSON.parse(JSON.stringify(data.check_items)) : [];
    // 需求2.5.3: 初始化总体检测结果
    editForm.check_result = data.check_result || '';
    // 初始化报告URL
    editForm.report_url = data.check_result_url || '';
    // 从URL中提取报告名称
    if (data.check_result_url) {
      const urlParts = data.check_result_url.split('/');
      uploadedReportName.value = decodeURIComponent(urlParts[urlParts.length - 1]);
    } else {
      uploadedReportName.value = '';
    }
    // 清空文件列表
    reportFileList.value = [];
  } catch (error: any) {
    message.error('加载详情失败');
    router.push('/');
  } finally {
    loading.value = false;
  }
}

// 需求2.5.4: 保存所有修改（样品信息+检测项目+总体结果+报告）
async function handleSave() {
  if (!checkObject.value) return;

  saving.value = true;

  try {
    // Step 1: 上传检测报告（如果有新文件）
    let reportUrl = editForm.report_url;
    if (editForm.report_file) {
      try {
        const uploadResult = await uploadReport(editForm.report_file);
        reportUrl = uploadResult.file_url;
        // 更新报告信息
        editForm.report_url = uploadResult.file_url;
        uploadedReportName.value = uploadResult.filename;
        message.success('报告上传成功');
      } catch (error: any) {
        message.error('报告上传失败: ' + (error.response?.data?.detail || error.message));
        saving.value = false;
        return;
      }
    }

    // Step 2: 保存所有修改
    await updateCheckObject(checkObject.value.id, {
      // 样品基本信息（所有字段都可编辑）
      sample_name: editForm.sample_name,
      company_name: editForm.company_name,
      remark: editForm.remark,
      check_object_union_num: editForm.check_object_union_num,
      check_type: editForm.check_type,
      submission_person: editForm.submission_person,
      submission_person_mobile: editForm.submission_person_mobile,
      submission_goods_car_number: editForm.submission_goods_car_number,
      // 日期字段转换为字符串
      create_time: editForm.create_time ? editForm.create_time.format('YYYY-MM-DD HH:mm:ss') : null,
      // 需求2.5.1: 新增字段
      commission_unit_address: editForm.commission_unit_address,
      production_date: editForm.production_date ? editForm.production_date.format('YYYY-MM-DD') : '/',
      sample_quantity: editForm.sample_quantity,
      inspection_date: editForm.inspection_date ? editForm.inspection_date.format('YYYY-MM-DD') : null,
      // 需求2.5.3: 总体检测结果和报告URL
      check_result: editForm.check_result,
      check_result_url: reportUrl,
      // 需求2.5.2: 检测项目
      check_items: editForm.check_items.map(item => ({
        id: item.id,
        check_item_name: item.check_item_name,
        check_method: item.check_method,
        unit: item.unit,
        num: item.num,
        detection_limit: item.detection_limit,
      })),
    });

    // Step 3: 如果有总体检测结果或检测项目结果，调用saveCheckResult
    if (editForm.check_result || editForm.check_items.some(item => item.num)) {
      await saveCheckResult(checkObject.value.id, {
        check_result: editForm.check_result,
        check_items: editForm.check_items.map(item => ({
          id: item.id,
          num: item.num || '',
          result: item.result || '',
        })),
      });
    }

    message.success('保存成功');
    // 清空文件列表和临时文件
    reportFileList.value = [];
    editForm.report_file = null;
    loadDetail();
  } catch (error: any) {
    message.error('保存失败: ' + (error.response?.data?.detail || error.message));
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

// 下载检测报告
function handleDownloadReport() {
  if (!editForm.report_url) {
    message.error('没有可下载的报告');
    return;
  }

  // 创建一个隐藏的a标签来触发下载
  const link = document.createElement('a');
  link.href = editForm.report_url;
  link.download = uploadedReportName.value || '检测报告.pdf';
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// 需求2.5.3: 报告文件上传校验
function beforeUploadReport(file: File) {
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
  // Store file in editForm
  editForm.report_file = file;
  return false; // Prevent auto upload
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
