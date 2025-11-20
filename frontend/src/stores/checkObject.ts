import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getCheckObjects, type CheckObject, type CheckObjectQuery } from '@/services/checkService';

interface QueryFilters {
  status: number | null;
  company: string;
  checkNo: string;
  startDate: string | null;
  endDate: string | null;
  checkResult: string | null;  // 需求2.3: 检测结果筛选
}

export const useCheckObjectStore = defineStore('checkObject', () => {
  // State
  const checkObjects = ref<CheckObject[]>([]);
  const total = ref<number>(0);
  const page = ref<number>(1);
  const pageSize = ref<number>(10);
  const loading = ref<boolean>(false);
  const filters = ref<QueryFilters>({
    status: null,
    company: '',
    checkNo: '',
    startDate: null,
    endDate: null,
    checkResult: null,
  });

  // Computed
  const hasFilters = computed(() => {
    return (
      filters.value.status !== null ||
      filters.value.company !== '' ||
      filters.value.checkNo !== '' ||
      filters.value.startDate !== null ||
      filters.value.endDate !== null ||
      filters.value.checkResult !== null
    );
  });

  // Actions
  async function fetchCheckObjects() {
    loading.value = true;

    try {
      const query: CheckObjectQuery = {
        page: page.value,
        page_size: pageSize.value,
      };

      if (filters.value.status !== null) {
        query.status = filters.value.status;
      }
      if (filters.value.company) {
        query.company = filters.value.company;
      }
      if (filters.value.checkNo) {
        query.check_no = filters.value.checkNo;
      }
      if (filters.value.startDate) {
        query.start_date = filters.value.startDate;
      }
      if (filters.value.endDate) {
        query.end_date = filters.value.endDate;
      }
      if (filters.value.checkResult) {
        query.check_result = filters.value.checkResult;
      }

      const result = await getCheckObjects(query);
      checkObjects.value = result.items;
      total.value = result.total;
      page.value = result.page;
      pageSize.value = result.page_size;
    } finally {
      loading.value = false;
    }
  }

  function setFilter(key: keyof QueryFilters, value: any) {
    (filters.value as any)[key] = value;
  }

  function setFilters(newFilters: Partial<QueryFilters>) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function resetFilters() {
    filters.value = {
      status: null,
      company: '',
      checkNo: '',
      startDate: null,
      endDate: null,
      checkResult: null,
    };
    page.value = 1;
  }

  function setPage(newPage: number) {
    page.value = newPage;
  }

  function setPageSize(newPageSize: number) {
    pageSize.value = newPageSize;
    page.value = 1; // Reset to first page
  }

  return {
    // State
    checkObjects,
    total,
    page,
    pageSize,
    loading,
    filters,
    // Computed
    hasFilters,
    // Actions
    fetchCheckObjects,
    setFilter,
    setFilters,
    resetFilters,
    setPage,
    setPageSize,
  };
});
