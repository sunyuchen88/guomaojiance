/**
 * Application constants
 */

// Status mappings for check objects
export const CHECK_STATUS = {
  PENDING: 0, // 待检测
  CHECKED: 1, // 已检测
  SUBMITTED: 2, // 已提交
} as const;

export const CHECK_STATUS_TEXT: Record<number, string> = {
  [CHECK_STATUS.PENDING]: '待检测',
  [CHECK_STATUS.CHECKED]: '已检测',
  [CHECK_STATUS.SUBMITTED]: '已提交',
};

export const CHECK_STATUS_COLOR: Record<number, string> = {
  [CHECK_STATUS.PENDING]: 'orange',
  [CHECK_STATUS.CHECKED]: 'blue',
  [CHECK_STATUS.SUBMITTED]: 'green',
};

// Result mappings
export const CHECK_RESULT = {
  PASS: '合格',
  FAIL: '不合格',
} as const;

// Sync type mappings
export const SYNC_TYPE = {
  AUTO: 'auto',
  MANUAL: 'manual',
} as const;

export const SYNC_TYPE_TEXT: Record<string, string> = {
  [SYNC_TYPE.AUTO]: '自动同步',
  [SYNC_TYPE.MANUAL]: '手动同步',
};

// Sync status mappings
export const SYNC_STATUS = {
  SUCCESS: 'success',
  FAILED: 'failed',
  IN_PROGRESS: 'in_progress',
} as const;

export const SYNC_STATUS_TEXT: Record<string, string> = {
  [SYNC_STATUS.SUCCESS]: '成功',
  [SYNC_STATUS.FAILED]: '失败',
  [SYNC_STATUS.IN_PROGRESS]: '进行中',
};

export const SYNC_STATUS_COLOR: Record<string, string> = {
  [SYNC_STATUS.SUCCESS]: 'green',
  [SYNC_STATUS.FAILED]: 'red',
  [SYNC_STATUS.IN_PROGRESS]: 'blue',
};

// File constraints
export const MAX_FILE_SIZE_MB = 10;
export const ALLOWED_FILE_TYPES = ['application/pdf'];

// Pagination defaults
export const DEFAULT_PAGE_SIZE = 50;
export const MAX_PAGE_SIZE = 50;
