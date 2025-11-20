<template>
  <div class="dashboard-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="logo">食品质检系统</div>
        <div class="user-info">
          <a-space>
            <span>{{ userStore.user?.name }}</span>
            <a-button type="link" @click="handleLogout">退出登录</a-button>
          </a-space>
        </div>
      </a-layout-header>
      <a-layout-content class="content">
        <a-card title="检测样品列表">
          <template #extra>
            <a-space>
              <DataSyncButton @success="handleSyncSuccess" />
              <ExportButton :filters="exportFilters" @success="handleExportSuccess" />
              <router-link to="/reports">
                <a-button>报告管理</a-button>
              </router-link>
            </a-space>
          </template>

          <!-- Query Filter -->
          <QueryFilter
            v-model="filterValues"
            @search="handleSearch"
            @reset="handleReset"
          />

          <!-- Result Summary -->
          <div v-if="checkObjectStore.hasFilters && !checkObjectStore.loading" class="result-summary">
            找到 {{ checkObjectStore.total }} 条结果
          </div>

          <!-- T167: Loading Skeleton -->
          <a-skeleton v-if="checkObjectStore.loading" active :paragraph="{ rows: 8 }" />

          <!-- T166: Empty State -->
          <a-empty
            v-else-if="checkObjectStore.checkObjects.length === 0"
            description="暂无数据"
          >
            <template #image>
              <inbox-outlined style="font-size: 64px; color: #d9d9d9;" />
            </template>
            <a-button v-if="checkObjectStore.hasFilters" type="primary" @click="handleReset">
              清除筛选条件
            </a-button>
          </a-empty>

          <!-- Data Table -->
          <PaginationTable
            v-else
            :columns="columns"
            :data-source="checkObjectStore.checkObjects"
            :loading="checkObjectStore.loading"
            :total="checkObjectStore.total"
            :page="checkObjectStore.page"
            :page-size="checkObjectStore.pageSize"
            @change="handlePaginationChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'sampling_time'">
                {{ formatDate(record.sampling_time) }}
              </template>
              <template v-else-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click="handleViewDetail(record.id)">
                    查看详情
                  </a-button>
                  <DownloadButton
                    v-if="record.report_url"
                    :check-no="record.check_no"
                    :report-url="record.report_url"
                    size="small"
                  />
                </a-space>
              </template>
            </template>
          </PaginationTable>
        </a-card>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
/**
 * DashboardView - Main view for check objects list
 * T096: Sample list, filters, sync button, pagination
 * T149: Download report button
 * T150: Export Excel button
 * T165: Search result summary
 * T166: Empty state
 * T167: Loading skeleton
 */
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { InboxOutlined } from '@ant-design/icons-vue';
import { useUserStore } from '@/stores/user';
import { useCheckObjectStore } from '@/stores/checkObject';
import { logout as logoutApi } from '@/services/authService';
import { getStatusText, getStatusColor, type ExportExcelParams } from '@/services/checkService';
import type { SyncResponse } from '@/services/syncService';
import DataSyncButton from '@/components/DataSyncButton.vue';
import QueryFilter from '@/components/QueryFilter.vue';
import PaginationTable from '@/components/PaginationTable.vue';
import ExportButton from '@/components/ExportButton.vue';
import DownloadButton from '@/components/DownloadButton.vue';
import dayjs from 'dayjs';

const router = useRouter();
const userStore = useUserStore();
const checkObjectStore = useCheckObjectStore();

const filterValues = computed({
  get() {
    return {
      status: checkObjectStore.filters.status,
      company: checkObjectStore.filters.company,
      checkNo: checkObjectStore.filters.checkNo,
      startDate: checkObjectStore.filters.startDate,
      endDate: checkObjectStore.filters.endDate,
    };
  },
  set(value) {
    checkObjectStore.setFilters(value);
  },
});

// T150: Export filters for Excel export
const exportFilters = computed<ExportExcelParams>(() => {
  const filters: ExportExcelParams = {};

  if (checkObjectStore.filters.status !== null) {
    filters.status = checkObjectStore.filters.status;
  }
  if (checkObjectStore.filters.company) {
    filters.company = checkObjectStore.filters.company;
  }
  if (checkObjectStore.filters.checkNo) {
    filters.check_no = checkObjectStore.filters.checkNo;
  }
  if (checkObjectStore.filters.startDate) {
    filters.start_date = checkObjectStore.filters.startDate;
  }
  if (checkObjectStore.filters.endDate) {
    filters.end_date = checkObjectStore.filters.endDate;
  }

  return filters;
});

const columns = [
  {
    title: '检测编号',
    dataIndex: 'check_no',
    key: 'check_no',
    width: 150,
  },
  {
    title: '样品名称',
    dataIndex: 'sample_name',
    key: 'sample_name',
    width: 150,
  },
  {
    title: '公司/个体',
    dataIndex: 'company_name',
    key: 'company_name',
    width: 180,
  },
  {
    title: '采样时间',
    dataIndex: 'sampling_time',
    key: 'sampling_time',
    width: 160,
  },
  {
    title: '状态',
    key: 'status',
    dataIndex: 'status',
    width: 100,
  },
  {
    title: '检验结果',
    dataIndex: 'check_result',
    key: 'check_result',
    width: 120,
  },
  {
    title: '操作',
    key: 'action',
    fixed: 'right',
    width: 120,
  },
];

onMounted(() => {
  loadData();
});

async function loadData() {
  try {
    await checkObjectStore.fetchCheckObjects();
  } catch (error: any) {
    message.error('加载数据失败');
  }
}

async function handleLogout() {
  try {
    await logoutApi();
    userStore.logout();
    message.success('已退出登录');
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
    userStore.logout();
    router.push('/login');
  }
}

function handleSyncSuccess(result: SyncResponse) {
  // Reload data after successful sync
  loadData();
}

function handleExportSuccess() {
  // Export completed, no need to reload data
  message.success('导出完成');
}

function handleSearch() {
  checkObjectStore.setPage(1);
  loadData();
}

function handleReset() {
  checkObjectStore.resetFilters();
  loadData();
}

function handlePaginationChange(pagination: { page: number; pageSize: number }) {
  checkObjectStore.setPage(pagination.page);
  checkObjectStore.setPageSize(pagination.pageSize);
  loadData();
}

function handleViewDetail(id: number) {
  router.push(`/check-detail/${id}`);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm');
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #001529;
  padding: 0 24px;
}

.logo {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.user-info {
  color: #fff;
}

.content {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);
}

.result-summary {
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  color: #0050b3;
}
</style>
