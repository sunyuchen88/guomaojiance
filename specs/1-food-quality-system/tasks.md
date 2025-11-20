# Tasks: 食品质检系统

**Input**: Design documents from `/specs/1-food-quality-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-summary.md

**Tests**: 根据项目宪章,TDD(测试驱动开发)是强制性的。测试任务必须包含在实施计划中,且测试必须在实现代码之前编写。测试覆盖率要求:总体 ≥ 80%,关键业务逻辑 = 100%。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

本项目采用前后端分离架构:
- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Database**: `backend/alembic/`
- **Documentation**: `specs/1-food-quality-system/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure (backend/app/{api,models,schemas,services,tasks,utils,middleware}/)
- [X] T002 Create frontend project structure (frontend/src/{views,components,stores,services,router,utils}/)
- [X] T003 [P] Initialize Python backend with requirements.txt (FastAPI, SQLAlchemy, Alembic, Pydantic, APScheduler, httpx, openpyxl, pytest)
- [X] T004 [P] Initialize Vue 3 frontend with package.json (Vue 3, Ant Design Vue, Vue Router, Pinia, Axios, Vite, xlsx, Vitest)
- [X] T005 [P] Configure backend linting (flake8, mypy) in backend/.flake8 and backend/mypy.ini
- [X] T006 [P] Configure frontend linting (ESLint, Prettier) in frontend/.eslintrc.js and frontend/.prettierrc
- [X] T007 Create docker-compose.yml with backend, frontend, PostgreSQL services
- [X] T008 Create backend/Dockerfile with Python 3.11 base image
- [X] T009 Create frontend/Dockerfile with Node.js 18 base image
- [X] T010 Create backend/.env.example with environment variables template
- [X] T011 Create frontend/.env.example with API base URL template
- [X] T012 Create .gitignore for Python, Node.js, and environment files
- [X] T013 Create README.md with project overview and quickstart instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [X] T014 Setup Alembic in backend/alembic/ with env.py and alembic.ini
- [X] T015 Create database connection in backend/app/database.py (SQLAlchemy engine, session factory)
- [X] T016 Create users table migration in backend/alembic/versions/001_create_users.py
- [X] T017 Create check_objects table migration in backend/alembic/versions/002_create_check_objects.py
- [X] T018 Create check_object_items table migration in backend/alembic/versions/003_create_check_object_items.py
- [X] T019 Create check_items table migration in backend/alembic/versions/004_create_check_items.py
- [X] T020 Create sync_logs table migration in backend/alembic/versions/005_create_sync_logs.py
- [X] T021 Create system_config table migration in backend/alembic/versions/006_create_system_config.py
- [X] T022 Create seed data migration in backend/alembic/versions/007_seed_data.py (default admin user, system config)

### Backend Models

- [X] T023 [P] Create User model in backend/app/models/user.py (id, username, password_hash, name, role, created_at, last_login_at)
- [X] T024 [P] Create CheckObject model in backend/app/models/check_object.py (21 fields per data-model.md)
- [X] T025 [P] Create CheckObjectItem model in backend/app/models/check_item.py (检测项目明细)
- [X] T026 [P] Create CheckItem model in backend/app/models/check_item.py (检测项目基础表)
- [X] T027 [P] Create SyncLog model in backend/app/models/sync_log.py (sync_type, status, fetched_count)
- [X] T028 [P] Create SystemConfig model in backend/app/models/system_config.py (API credentials, sync interval)
- [X] T029 Create models __init__.py exporting all models in backend/app/models/__init__.py

### Backend Schemas (Pydantic)

- [X] T030 [P] Create UserSchema in backend/app/schemas/user.py (UserLogin, UserResponse, TokenResponse)
- [X] T031 [P] Create CheckObjectSchema in backend/app/schemas/check_object.py (CheckObjectList, CheckObjectDetail, CheckObjectUpdate)
- [X] T032 [P] Create CheckResultSchema in backend/app/schemas/check_result.py (CheckResultInput, CheckItemResult)
- [X] T033 [P] Create SyncSchema in backend/app/schemas/sync_log.py (SyncRequest, SyncResponse, SyncLogList)
- [X] T034 Create schemas __init__.py in backend/app/schemas/__init__.py

### Backend Core Infrastructure

- [X] T035 Create configuration management in backend/app/config.py (load env vars, database URL, JWT secret)
- [X] T036 Create security utilities in backend/app/utils/security.py (bcrypt password hash, JWT encode/decode, MD5 signature)
- [X] T037 Create pagination helper in backend/app/utils/pagination.py (paginate function, PaginatedResponse schema)
- [X] T038 Create storage monitoring utility in backend/app/utils/storage.py (check disk space, alert if <10GB)
- [X] T039 Create authentication dependency in backend/app/api/deps.py (get_current_user, require_admin)
- [X] T040 Create database session dependency in backend/app/api/deps.py (get_db)
- [X] T041 Create performance middleware in backend/app/middleware/performance.py (log response time)
- [X] T042 Create error handling middleware in backend/app/middleware/error_handler.py (global exception handler)
- [X] T043 Create FastAPI app initialization in backend/app/main.py (CORS, middleware, static files, router registration)

### Frontend Core Infrastructure

- [X] T044 Create Axios instance in frontend/src/services/api.ts (base URL, request/response interceptors)
- [X] T045 Create HTTP interceptors in frontend/src/utils/request.ts (add JWT token, handle 401 errors)
- [X] T046 Create constants file in frontend/src/utils/constants.ts (status mappings, API endpoints)
- [X] T047 Create user store in frontend/src/stores/user.ts (login state, user info, logout action)
- [X] T048 Create checkObject store in frontend/src/stores/checkObject.ts (sample list, filters, pagination)
- [X] T049 Create Vue Router configuration in frontend/src/router/index.ts (routes, auth guard)
- [X] T050 Create App.vue root component in frontend/src/App.vue (router-view, global layout)
- [X] T051 Create main.ts entry point in frontend/src/main.ts (Vue app, Ant Design Vue, Pinia, Router)

### Testing Infrastructure

- [X] T052 [P] Create pytest configuration in backend/pytest.ini (test paths, coverage settings)
- [X] T053 [P] Create pytest fixtures in backend/tests/conftest.py (test database, test client, mock data)
- [X] T054 [P] Create Vitest configuration in frontend/vite.config.ts (test environment, coverage)
- [X] T055 [P] Create test utilities in frontend/tests/utils/index.ts (mount helpers, mock stores)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 6 - 账号密码登录认证 (Priority: P1) 🎯 MVP

**Goal**: 实现账号密码登录功能,确保只有授权人员能够访问系统,2小时会话超时

**Independent Test**: 用户可以访问登录页,输入正确账号密码后跳转至主页,输入错误信息时显示错误提示,2小时后自动退出

**Why First**: 所有其他功能都需要用户登录后才能访问,这是最基础的前置依赖

### Tests for User Story 6 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [X] T056 [P] [US6] Contract test for POST /auth/login in backend/tests/contract/test_auth_api.py (test valid login, invalid credentials, missing fields)
- [X] T057 [P] [US6] Unit test for authentication service in backend/tests/unit/test_auth_service.py (test password verification, token generation)
- [X] T058 [P] [US6] Integration test for login flow in backend/tests/integration/test_auth_flow.py (test complete login journey, session timeout)
- [X] T059 [P] [US6] Component test for LoginView in frontend/tests/unit/components/LoginView.spec.ts (test form validation, submit action)

### Implementation for User Story 6

- [X] T060 [P] [US6] Implement AuthService in backend/app/services/auth_service.py (verify_credentials, create_access_token, decode_token)
- [X] T061 [US6] Implement POST /auth/login endpoint in backend/app/api/auth.py (accept username/password, return JWT + user info)
- [X] T062 [US6] Implement logout endpoint in backend/app/api/auth.py (optional - client-side token removal)
- [X] T063 [US6] Update last_login_at timestamp in User model on successful login in backend/app/services/auth_service.py
- [X] T064 [P] [US6] Create authService.ts in frontend/src/services/authService.ts (login, logout API calls)
- [X] T065 [P] [US6] Create LoginView.vue in frontend/src/views/LoginView.vue (username/password form, Ant Design validation)
- [X] T066 [US6] Implement login action in user store in frontend/src/stores/user.ts (call API, save token, update state)
- [X] T067 [US6] Implement logout action in user store in frontend/src/stores/user.ts (clear token, redirect to login)
- [X] T068 [US6] Add authentication guard in Vue Router in frontend/src/router/index.ts (redirect to login if no token)
- [X] T069 [US6] Add automatic logout after 2 hours in frontend/src/utils/request.ts (check token expiry in interceptor)
- [X] T070 [US6] Add error handling for login failures in frontend/src/views/LoginView.vue (display error messages)

**Checkpoint**: At this point, users can log in and be authenticated. All subsequent features depend on this.

---

## Phase 4: User Story 1 - 检测数据获取与同步 (Priority: P1) 🎯 MVP

**Goal**: 检测人员可以从客户系统获取待检测样品信息,支持自动定时同步(30分钟)+手动触发,查看和编辑样品详细信息

**Independent Test**: 登录系统 → 点击获取数据 → 查看样品列表 → 编辑检测信息 → 保存成功

### Tests for User Story 1 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [X] T071 [P] [US1] Contract test for POST /sync/fetch in backend/tests/contract/test_sync_api.py (test manual sync, concurrent control)
- [X] T072 [P] [US1] Contract test for GET /sync/logs in backend/tests/contract/test_sync_api.py (test pagination, filtering)
- [X] T073 [P] [US1] Contract test for GET /check-objects in backend/tests/contract/test_check_api.py (test query filters, pagination)
- [X] T074 [P] [US1] Contract test for GET /check-objects/{id} in backend/tests/contract/test_check_api.py (test detail retrieval)
- [X] T075 [P] [US1] Contract test for PUT /check-objects/{id} in backend/tests/contract/test_check_api.py (test edit sample info)
- [X] T076 [P] [US1] Integration test for client API service in backend/tests/integration/test_client_api.py (mock client API, test data fetch)
- [X] T077 [P] [US1] Unit test for sync service in backend/tests/unit/test_sync_service.py (test concurrency control, error handling)
- [X] T078 [P] [US1] Unit test for APScheduler task in backend/tests/unit/test_scheduler.py (test job registration, execution)
- [X] T079 [P] [US1] Component test for DashboardView in frontend/tests/unit/components/DashboardView.spec.ts (test list rendering, filters)
- [X] T080 [P] [US1] Component test for DataSyncButton in frontend/tests/unit/components/DataSyncButton.spec.ts (test click action, loading state)

### Implementation for User Story 1

- [X] T081 [P] [US1] Implement ClientAPIService in backend/app/services/client_api_service.py (fetch_check_objects, calculate MD5 signature)
- [X] T082 [P] [US1] Implement SyncService in backend/app/services/sync_service.py (sync_data, handle concurrency, log results)
- [X] T083 [US1] Add sync lock mechanism in SyncService in backend/app/services/sync_service.py (prevent duplicate syncs)
- [X] T084 [US1] Implement APScheduler setup in backend/app/tasks/scheduler.py (30-minute interval job calling SyncService)
- [X] T085 [US1] Implement POST /sync/fetch endpoint in backend/app/api/sync.py (manual trigger, call SyncService)
- [X] T086 [US1] Implement GET /sync/logs endpoint in backend/app/api/sync.py (pagination, return sync history)
- [X] T087 [US1] Implement GET /check-objects endpoint in backend/app/api/check_objects.py (query filters: status, company, check_no, date range, pagination)
- [X] T088 [US1] Implement GET /check-objects/{id} endpoint in backend/app/api/check_objects.py (return detailed sample info with check_items)
- [X] T089 [US1] Implement PUT /check-objects/{id} endpoint in backend/app/api/check_objects.py (update sample info and check_items)
- [X] T090 [US1] Add scheduler startup in backend/app/main.py (start APScheduler on app startup)
- [X] T091 [P] [US1] Create syncService.ts in frontend/src/services/syncService.ts (fetchData, getSyncLogs API calls)
- [X] T092 [P] [US1] Create checkService.ts in frontend/src/services/checkService.ts (getCheckObjects, getCheckObjectDetail, updateCheckObject API calls)
- [X] T093 [P] [US1] Create DataSyncButton.vue in frontend/src/components/DataSyncButton.vue (trigger manual sync, show loading state)
- [X] T094 [P] [US1] Create QueryFilter.vue in frontend/src/components/QueryFilter.vue (status, company, check_no, date range filters)
- [X] T095 [P] [US1] Create PaginationTable.vue in frontend/src/components/PaginationTable.vue (reusable table with pagination)
- [X] T096 [US1] Create DashboardView.vue in frontend/src/views/DashboardView.vue (sample list, filters, sync button, pagination)
- [X] T097 [US1] Create CheckDetailView.vue in frontend/src/views/CheckDetailView.vue (edit sample info, check_items table)
- [X] T098 [US1] Update checkObject store with filter state in frontend/src/stores/checkObject.ts (save filter conditions, pagination state)
- [X] T099 [US1] Add success/error notifications in DashboardView in frontend/src/views/DashboardView.vue (sync result, edit result)

**Checkpoint**: At this point, users can fetch sample data, view lists, and edit sample information. System auto-syncs every 30 minutes.

---

## Phase 5: User Story 2 - 检测结果录入与报告上传 (Priority: P1) 🎯 MVP

**Goal**: 检测人员完成检测后,录入检测结果(3个核心字段)和上传PDF报告

**Independent Test**: 选择样品 → 点击检测结果修改 → 填写检测项目/结果/指标 → 上传PDF报告 → 保存成功

### Tests for User Story 2 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [X] T100 [P] [US2] Contract test for PUT /check-objects/{id}/result in backend/tests/contract/test_check_result_api.py (test result input, validation)
- [X] T101 [P] [US2] Contract test for POST /reports/upload in backend/tests/contract/test_report_api.py (test PDF upload, file size limit, format validation)
- [X] T102 [P] [US2] Integration test for file upload in backend/tests/integration/test_file_upload.py (test file storage, URL generation)
- [X] T103 [P] [US2] Unit test for file service in backend/tests/unit/test_file_service.py (test path generation, storage logic)
- [X] T104 [P] [US2] Component test for CheckResultForm in frontend/tests/unit/components/CheckResultForm.spec.ts (test form validation, result input)
- [X] T105 [P] [US2] Component test for ReportUpload in frontend/tests/unit/components/ReportUpload.spec.ts (test file selection, upload action)

### Implementation for User Story 2

- [X] T106 [P] [US2] Implement FileService in backend/app/services/file_service.py (save_pdf_report, generate_file_path, generate_url)
- [X] T107 [US2] Create uploads directory structure in backend/uploads/reports/{year}/{month}/
- [X] T108 [US2] Implement PUT /check-objects/{id}/result endpoint in backend/app/api/check_objects.py (save check_result, check_items results, update status to 1)
- [X] T109 [US2] Implement POST /reports/upload endpoint in backend/app/api/reports.py (accept multipart/form-data, validate PDF, save to disk, generate URL)
- [X] T110 [US2] Add file size validation in reports.upload in backend/app/api/reports.py (reject files >10MB)
- [X] T111 [US2] Add PDF format validation in reports.upload in backend/app/api/reports.py (check MIME type and extension)
- [X] T112 [US2] Configure static file serving in backend/app/main.py (mount /reports directory for HTTP access)
- [X] T113 [P] [US2] Create CheckResultForm.vue in frontend/src/components/CheckResultForm.vue (3 fields: check_item, result dropdown, indicator)
- [X] T114 [P] [US2] Create ReportUpload.vue in frontend/src/components/ReportUpload.vue (PDF file selector, upload button, progress indicator)
- [X] T115 [US2] Add result input modal in CheckDetailView in frontend/src/views/CheckDetailView.vue (open form, submit result)
- [X] T116 [US2] Implement saveCheckResult in checkService.ts in frontend/src/services/checkService.ts (API call to save result)
- [X] T117 [US2] Implement uploadReport in checkService.ts in frontend/src/services/checkService.ts (API call to upload PDF)
- [X] T118 [US2] Add file upload progress indicator in ReportUpload in frontend/src/components/ReportUpload.vue (Ant Design Upload progress)
- [X] T119 [US2] Add success notification after result save in CheckDetailView in frontend/src/views/CheckDetailView.vue (display confirmation)

**Checkpoint**: At this point, users can input test results and upload PDF reports. Samples transition from status 0 to 1.

---

## Phase 6: User Story 3 - 检测结果提交至客户系统 (Priority: P1) 🎯 MVP

**Goal**: 检测人员将完整的检测结果和报告提交至客户方API,处理成功和失败响应

**Independent Test**: 选择已检测样品 → 点击提交检测结果 → 确认提交 → 系统调用客户API → 更新状态

### Tests for User Story 3 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [x] T120 [P] [US3] Contract test for POST /submit/{check_object_id} in backend/tests/contract/test_submit_api.py (test successful submission, failure handling)
- [x] T121 [P] [US3] Integration test for submit service in backend/tests/integration/test_client_api.py (mock client API feedback endpoint, test status 200/400)
- [x] T122 [P] [US3] Unit test for submit service in backend/tests/unit/test_submit_service.py (test data formatting, signature generation)
- [x] T123 [P] [US3] Component test for submit confirmation modal in frontend/tests/unit/components/SubmitModal.spec.ts (test confirmation dialog, submit action)

### Implementation for User Story 3

- [x] T124 [P] [US3] Implement SubmitService in backend/app/services/submit_service.py (format_check_result, call_client_api, handle_response)
- [x] T125 [US3] Add MD5 signature generation in SubmitService in backend/app/services/submit_service.py (calculate sign parameter)
- [x] T126 [US3] Implement POST /submit/{check_object_id} endpoint in backend/app/api/submit.py (validate status=1, call SubmitService, update status to 2)
- [x] T127 [US3] Add error handling for client API failures in submit.py in backend/app/api/submit.py (return 400 with client error message)
- [x] T128 [US3] Add retry logic for network failures in SubmitService in backend/app/services/submit_service.py (retry 3 times with exponential backoff)
- [x] T129 [P] [US3] Create SubmitModal.vue in frontend/src/components/SubmitModal.vue (confirmation dialog, show result summary)
- [x] T130 [US3] Add submit button in CheckDetailView in frontend/src/views/CheckDetailView.vue (open SubmitModal, trigger submission)
- [x] T131 [US3] Implement submitResult in checkService.ts in frontend/src/services/checkService.ts (API call to submit result)
- [x] T132 [US3] Add success/failure handling in CheckDetailView in frontend/src/views/CheckDetailView.vue (show success message or error details)
- [x] T133 [US3] Add status badge in DashboardView in frontend/src/views/DashboardView.vue (display 待检测/已检测/已提交 with colors)

**Checkpoint**: At this point, users can submit test results to client API. Complete inspection workflow (fetch → test → submit) is functional.

---

## Phase 7: User Story 4 - 检测数据导出与下载 (Priority: P2)

**Goal**: 用户可以下载已上传的PDF检测报告和导出Excel检测结果(8个字段)

**Independent Test**: 选择样品 → 下载PDF报告 → 成功获得文件; 选择样品 → 导出Excel → 获得格式正确的Excel文件

### Tests for User Story 4 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [x] T134 [P] [US4] Contract test for GET /reports/download/{check_no} in backend/tests/contract/test_report_api.py (test PDF download, 404 for missing report)
- [x] T135 [P] [US4] Contract test for POST /reports/export-excel in backend/tests/contract/test_report_api.py (test Excel export with check_object_ids, query filters, 1000-row limit)
- [x] T136 [P] [US4] Integration test for Excel export in backend/tests/integration/test_excel_export.py (test openpyxl file generation, verify 8 columns, multiple items per sample)
- [x] T137 [P] [US4] Unit test for Excel export service in backend/tests/unit/test_excel_service.py (test row expansion logic, column formatting)
- [x] T138 [P] [US4] Component test for export button in frontend/tests/unit/components/ExportButton.spec.ts (test download action, loading state)

### Implementation for User Story 4

- [x] T139 [P] [US4] Implement ExcelExportService in backend/app/services/excel_service.py (generate_excel, expand_check_items_to_rows)
- [x] T140 [US4] Add openpyxl workbook generation in ExcelExportService in backend/app/services/excel_service.py (create headers, format cells)
- [x] T141 [US4] Implement GET /reports/download/{check_no} endpoint in backend/app/api/reports.py (find file, return FileResponse)
- [x] T142 [US4] Implement POST /reports/export-excel endpoint in backend/app/api/reports.py (accept check_object_ids or query, generate Excel, return file stream)
- [x] T143 [US4] Add 1000-row limit validation in reports.export_excel in backend/app/api/reports.py (return 400 if exceeds limit)
- [x] T144 [US4] Add query filter logic in reports.export_excel in backend/app/api/reports.py (apply status, company, date range filters)
- [x] T145 [US4] Format Excel columns in ExcelExportService in backend/app/services/excel_service.py (样品名称, 公司/个体, 检测项目, 检验结果, 该项结果, 检测时间, 样品编号, 检测方法)
- [x] T146 [US4] Add Excel filename generation in reports.export_excel in backend/app/api/reports.py (检测结果导出_YYYYMMDD.xlsx)
- [x] T147 [P] [US4] Create ExportButton.vue in frontend/src/components/ExportButton.vue (trigger Excel export, download file)
- [x] T148 [P] [US4] Create DownloadButton.vue in frontend/src/components/DownloadButton.vue (trigger PDF download)
- [x] T149 [US4] Add download report button in DashboardView in frontend/src/views/DashboardView.vue (call downloadReport API)
- [x] T150 [US4] Add export Excel button in DashboardView in frontend/src/views/DashboardView.vue (call exportExcel API with selected IDs)
- [x] T151 [US4] Implement downloadReport in checkService.ts in frontend/src/services/checkService.ts (API call to download PDF)
- [x] T152 [US4] Implement exportExcel in checkService.ts in frontend/src/services/checkService.ts (API call to export Excel with query filters)
- [x] T153 [US4] Add file download handling in ExportButton in frontend/src/components/ExportButton.vue (trigger browser download with Content-Disposition)
- [x] T154 [US4] Add error handling for missing reports in DownloadButton in frontend/src/components/DownloadButton.vue (disable button if no report URL)

**Checkpoint**: At this point, users can download PDF reports and export Excel files with formatted test results.

---

## Phase 8: User Story 5 - 多维度查询与过滤 (Priority: P2)

**Goal**: 用户通过状态、公司名称、检测编号、采样时间等条件快速查找检测项目

**Independent Test**: 输入查询条件 → 点击查询 → 查看过滤后的结果列表 → 点击重置 → 显示全部样品

**Note**: 大部分查询功能已在 Phase 4 (US1) 实现,本阶段主要补充高级过滤和优化用户体验

### Tests for User Story 5 (按宪章要求强制执行) ✅

> **CRITICAL: 按照 TDD 原则,必须先写这些测试,确保它们失败后再开始实现**

- [x] T155 [P] [US5] Integration test for complex query combinations in backend/tests/integration/test_query_filters.py (test multi-condition filtering)
- [x] T156 [P] [US5] Component test for QueryFilter reset in frontend/tests/unit/components/QueryFilter.spec.ts (test reset button clears all filters)
- [ ] T157 [P] [US5] E2E test for query workflow in frontend/tests/e2e/query.spec.ts (optional - test complete filter → search → reset flow)

### Implementation for User Story 5

- [x] T158 [US5] Add company name fuzzy search in GET /check-objects in backend/app/api/check_objects.py (use ILIKE query)
- [x] T159 [US5] Add check_no exact search in GET /check-objects in backend/app/api/check_objects.py (exact match query)
- [x] T160 [US5] Add date range filter in GET /check-objects in backend/app/api/check_objects.py (start_date, end_date parameters)
- [x] T161 [US5] Add multi-condition query optimization in check_objects.py in backend/app/api/check_objects.py (combine filters efficiently)
- [x] T162 [US5] Add query result count in GET /check-objects response in backend/app/api/check_objects.py (return total count for "showing X of Y" UX)
- [x] T163 [US5] Add reset button in QueryFilter in frontend/src/components/QueryFilter.vue (clear all filter fields)
- [x] T164 [US5] Add filter persistence in checkObject store in frontend/src/stores/checkObject.ts (save filters across page navigation)
- [x] T165 [US5] Add search result summary in DashboardView in frontend/src/views/DashboardView.vue (display "找到 X 条结果")
- [x] T166 [US5] Add empty state in DashboardView in frontend/src/views/DashboardView.vue (show message when no results found)
- [x] T167 [US5] Add loading skeleton in DashboardView in frontend/src/views/DashboardView.vue (Ant Design Skeleton during query)

**Checkpoint**: At this point, users have a fully functional query and filter system with excellent UX.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, performance, accessibility, and production readiness

### Code Quality & Testing

- [x] T168 [P] Run flake8 linting on backend in backend/ (fix all violations, ensure ≤10 cyclomatic complexity)
- [x] T169 [P] Run mypy type checking on backend in backend/ (fix all type errors)
- [x] T170 [P] Run ESLint on frontend in frontend/ (fix all errors and warnings)
- [x] T171 [P] Run Prettier on frontend in frontend/ (format all code)
- [x] T172 [P] Verify test coverage ≥80% in backend using pytest-cov (check critical logic = 100%)
- [x] T173 [P] Verify test coverage ≥80% in frontend using Vitest coverage report
- [x] T174 [P] Add unit tests for edge cases in backend/tests/unit/ (empty lists, null values, boundary conditions)
- [x] T175 [P] Add unit tests for utility functions in frontend/tests/unit/utils/ (constants, helpers)

### Performance Optimization

- [x] T176 [P] Add database indexes verification in backend/alembic/ (ensure all indexes from data-model.md are created)
- [x] T177 [P] Run EXPLAIN ANALYZE on complex queries in backend (verify index usage, query plan efficiency)
- [x] T178 [US1] Optimize sample list query in check_objects.py (add eager loading for check_items if needed)
- [x] T179 [US4] Add streaming for large Excel exports in reports.py (use StreamingResponse for >100 rows)
- [x] T180 [P] Measure API response times in backend (verify P95 <200ms for simple, <500ms for complex)
- [x] T181 [P] Measure page load times in frontend (verify FCP <1.5s, LCP <2.5s using Lighthouse)
- [x] T182 [P] Add performance monitoring in backend/app/middleware/performance.py (log slow requests >500ms)
- [x] T183 [P] Add lazy loading for components in frontend/src/router/index.ts (code splitting for views)

### Security Hardening

- [x] T184 [P] Add SQL injection protection verification in backend (use parameterized queries, no string concatenation)
- [x] T185 [P] Add XSS protection in frontend (ensure all user inputs are escaped, use v-text over v-html)
- [x] T186 [P] Add CSRF protection in backend (CORS configuration, SameSite cookies)
- [x] T187 [P] Verify password hashing strength in security.py (bcrypt rounds ≥12)
- [x] T188 [P] Add rate limiting for login endpoint in backend/app/api/auth.py (prevent brute force attacks)
- [x] T189 [P] Add file upload security in reports.py (verify MIME type, sanitize filenames, restrict extensions)
- [x] T190 [P] Verify secrets are not committed in .env files (check .gitignore, remove any hardcoded secrets)

### Accessibility (WCAG 2.1 AA)

- [x] T191 [P] Add form labels in LoginView in frontend/src/views/LoginView.vue (ensure all inputs have <label>)
- [x] T192 [P] Add keyboard navigation support in DashboardView in frontend/src/views/DashboardView.vue (tab order, Enter to submit)
- [x] T193 [P] Add ARIA labels for buttons in frontend/src/components/ (aria-label for icon-only buttons)
- [x] T194 [P] Verify color contrast ratios in frontend (use contrast checker, ensure ≥4.5:1 for normal text)
- [x] T195 [P] Add focus indicators for interactive elements in frontend/src/styles/ (visible focus ring)
- [x] T196 [P] Test screen reader compatibility in frontend (test with NVDA or VoiceOver)

### User Feedback & Error Handling

- [x] T197 [P] Ensure all operations have <200ms visual feedback in frontend (loading spinners, button states)
- [x] T198 [P] Add error messages for all API failures in frontend/src/utils/request.ts (user-friendly error descriptions)
- [x] T199 [P] Add retry options for failed operations in frontend/src/components/ (retry button for sync/submit failures)
- [x] T200 [P] Add confirmation dialogs for destructive actions in frontend (delete, overwrite confirmations)
- [x] T201 [P] Add toast notifications for success/error in frontend/src/views/ (use Ant Design Message component)

### Documentation & Deployment

- [x] T202 [P] Update README.md with complete setup instructions
- [x] T203 [P] Validate quickstart.md instructions (test from clean environment)
- [x] T204 [P] Create API documentation in docs/api.md (or use FastAPI auto-generated docs)
- [x] T205 [P] Create deployment guide in docs/deployment.md (Docker Compose production setup)
- [x] T206 [P] Add inline code comments for complex logic in backend/app/services/ (explain business rules)
- [x] T207 [P] Add JSDoc comments for reusable components in frontend/src/components/

### Storage & Monitoring

- [x] T208 [US1] Add storage monitoring cron job in backend/app/tasks/scheduler.py (check disk space daily, alert if <10GB)
- [x] T209 [P] Add logging for sync failures in SyncService in backend/app/services/sync_service.py (detailed error messages)
- [x] T210 [P] Add logging for submit failures in SubmitService in backend/app/services/submit_service.py (record client API errors)
- [x] T211 [P] Create log rotation configuration in backend/ (rotate logs daily, keep 30 days)

### Final Validation

- [x] T212 Run complete test suite in backend (pytest backend/tests/)
- [x] T213 Run complete test suite in frontend (npm run test in frontend/)
- [x] T214 Build Docker images (docker-compose build)
- [x] T215 Start all services with docker-compose up
- [x] T216 Run alembic migrations (docker-compose exec backend alembic upgrade head)
- [x] T217 Test complete user workflows (login → fetch → test → submit → export)
- [x] T218 Verify quickstart.md works from clean environment
- [x] T219 Check constitution compliance (code quality ✓, TDD ✓, UX ✓, performance ✓)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3 (US6 - Login)**: Depends on Phase 2 completion - BLOCKS all other user stories (authentication required)
- **Phase 4 (US1 - Data Sync)**: Depends on Phase 3 completion - Can run in parallel with US2/US3 once auth is ready
- **Phase 5 (US2 - Result Input)**: Depends on Phase 3 completion - Can run in parallel with US1 once auth is ready
- **Phase 6 (US3 - Submit)**: Depends on Phase 5 completion (needs test results) - Sequential after US2
- **Phase 7 (US4 - Export)**: Depends on Phase 5 completion (needs test data) - Can run in parallel with US3
- **Phase 8 (US5 - Query)**: Depends on Phase 4 completion (enhances US1) - Can run in parallel with US2/US3/US4
- **Phase 9 (Polish)**: Depends on all desired user stories being complete

### User Story Execution Order

**Strict Sequential**:
```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US6 Login)
  → Phase 4 (US1 Data Sync) + Phase 5 (US2 Result Input) [parallel]
  → Phase 6 (US3 Submit) [needs US2]
  → Phase 7 (US4 Export) + Phase 8 (US5 Query) [parallel]
  → Phase 9 (Polish)
```

**Optimal Parallel** (with 3+ developers):
```
Phase 1 → Phase 2 → Phase 3 (US6)
  → Dev A: Phase 4 (US1) → Phase 8 (US5)
  → Dev B: Phase 5 (US2) → Phase 6 (US3)
  → Dev C: Phase 7 (US4)
  → All converge → Phase 9 (Polish)
```

### Within Each Phase

- **Tests MUST be written first** (TDD) - ensure they fail before implementing
- Models before services
- Services before API endpoints
- API endpoints before frontend services
- Frontend services before components
- Components before views
- Core implementation before integration

### Parallel Opportunities

- **Phase 1**: T003-T006, T008-T011 can run in parallel
- **Phase 2 Backend Models**: T023-T028 can run in parallel
- **Phase 2 Schemas**: T030-T033 can run in parallel
- **Phase 2 Frontend**: T044-T051 can run in parallel
- **Phase 2 Testing**: T052-T055 can run in parallel
- **All test tasks** within a user story marked [P] can run in parallel
- **User Stories**: US1, US2 can start together after US6; US4, US5 can run together after US2

---

## Implementation Strategy

### MVP First (Minimal Viable Product)

**Scope**: US6 (Login) + US1 (Data Sync) + US2 (Result Input) + US3 (Submit)

**Steps**:
1. Complete Phase 1 (Setup) - ~1 day
2. Complete Phase 2 (Foundational) - ~2-3 days
3. Complete Phase 3 (US6 Login) - ~1 day
4. Complete Phase 4 (US1 Data Sync) - ~2-3 days
5. Complete Phase 5 (US2 Result Input) - ~2 days
6. Complete Phase 6 (US3 Submit) - ~1-2 days
7. **STOP and VALIDATE**: Test complete inspection workflow independently
8. Deploy MVP (core workflow functional, no export/query features yet)

**MVP Delivers**: Complete inspection workflow - login → auto-sync data → input results → upload reports → submit to client

### Incremental Delivery

**Release 1.0 (MVP)**: Login + Data Sync + Result Input + Submit (Phases 1-6)
- **Value**: Core inspection workflow functional
- **Tasks**: T001-T133 (133 tasks)

**Release 1.1**: Add Export & Download (Phase 7)
- **Value**: PDF download + Excel export for reporting
- **Tasks**: T134-T154 (21 tasks)

**Release 1.2**: Add Advanced Query (Phase 8)
- **Value**: Improved search and filtering UX
- **Tasks**: T155-T167 (13 tasks)

**Release 1.3**: Polish & Production Ready (Phase 9)
- **Value**: Performance, security, accessibility, documentation
- **Tasks**: T168-T219 (52 tasks)

### Parallel Team Strategy

**With 3 Developers**:

1. **Week 1**: All together complete Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US6 Login)
2. **Week 2-3**: Split work once foundation ready:
   - **Developer A**: Phase 4 (US1 Data Sync) → backend sync service + scheduler
   - **Developer B**: Phase 5 (US2 Result Input) → file upload + result API
   - **Developer C**: Frontend components for US1 + US2
3. **Week 3-4**:
   - **Developer A**: Phase 8 (US5 Query) - enhance US1 with advanced filters
   - **Developer B**: Phase 6 (US3 Submit) - client API integration
   - **Developer C**: Phase 7 (US4 Export) - PDF download + Excel export
4. **Week 5**: All together complete Phase 9 (Polish) - testing, performance, docs

---

## Notes

- **[P]** markers indicate tasks that can run in parallel (different files, no dependencies)
- **[US#]** labels map tasks to specific user stories for traceability
- Each user story should be independently completable and testable
- **TDD is mandatory**: Write tests first, ensure they fail, then implement
- Test coverage: ≥80% overall, 100% for API calls, file upload, data submission
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- File paths are exact - adjust if project structure differs from plan.md

---

## Task Count Summary

- **Phase 1 (Setup)**: 13 tasks (T001-T013)
- **Phase 2 (Foundational)**: 42 tasks (T014-T055)
- **Phase 3 (US6 Login)**: 15 tasks (T056-T070)
- **Phase 4 (US1 Data Sync)**: 29 tasks (T071-T099)
- **Phase 5 (US2 Result Input)**: 20 tasks (T100-T119)
- **Phase 6 (US3 Submit)**: 14 tasks (T120-T133)
- **Phase 7 (US4 Export)**: 21 tasks (T134-T154)
- **Phase 8 (US5 Query)**: 13 tasks (T155-T167)
- **Phase 9 (Polish)**: 52 tasks (T168-T219)

**Total**: 219 tasks

**MVP Scope (Phases 1-6)**: 133 tasks
**Full Feature Set (Phases 1-8)**: 167 tasks
**Production Ready (All Phases)**: 219 tasks

---

**Generated**: 2025-11-19
**Specification**: specs/1-food-quality-system/spec.md
**Implementation Plan**: specs/1-food-quality-system/plan.md
