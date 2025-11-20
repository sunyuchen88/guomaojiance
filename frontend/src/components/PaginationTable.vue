<template>
  <a-table
    :columns="columns"
    :data-source="dataSource"
    :loading="loading"
    :pagination="paginationConfig"
    :row-key="rowKey"
    @change="handleTableChange"
  >
    <template v-for="(_, name) in $slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData" />
    </template>
  </a-table>
</template>

<script setup lang="ts">
/**
 * PaginationTable Component
 * T095: Reusable table with pagination
 */
import { computed } from 'vue';
import type { TableColumnType, TablePaginationConfig } from 'ant-design-vue';

interface Props {
  columns: TableColumnType[];
  dataSource: any[];
  loading?: boolean;
  total?: number;
  page?: number;
  pageSize?: number;
  rowKey?: string | ((record: any) => string | number);
  showSizeChanger?: boolean;
  pageSizeOptions?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  total: 0,
  page: 1,
  pageSize: 10,
  rowKey: 'id',
  showSizeChanger: true,
  pageSizeOptions: () => ['10', '20', '50', '100'],
});

const emit = defineEmits<{
  (e: 'update:page', page: number): void;
  (e: 'update:pageSize', pageSize: number): void;
  (e: 'change', pagination: { page: number; pageSize: number }): void;
}>();

const paginationConfig = computed<TablePaginationConfig>(() => ({
  current: props.page,
  pageSize: props.pageSize,
  total: props.total,
  showSizeChanger: props.showSizeChanger,
  pageSizeOptions: props.pageSizeOptions,
  showTotal: (total: number) => `共 ${total} 条`,
  showQuickJumper: true,
}));

function handleTableChange(pagination: any) {
  const newPage = pagination.current;
  const newPageSize = pagination.pageSize;

  emit('update:page', newPage);
  emit('update:pageSize', newPageSize);
  emit('change', { page: newPage, pageSize: newPageSize });
}
</script>
