# Implementation Plan: 食品质检系统

**Branch**: `1-food-quality-system` | **Date**: 2025-11-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-food-quality-system/spec.md`

## Summary

国贸食品科学研究院食品质检系统,用于对接客户方系统,实现检测样品数据自动获取、检测结果录入、PDF报告上传、检测结果自动提交和Excel数据导出的完整业务流程。系统采用前后端分离架构,后端使用Python FastAPI,前端使用Vue 3 + Ant Design Vue,数据库使用PostgreSQL,支持Docker容器化部署。

**核心业务流程**:

1. 从客户方API自动/手动获取待检测样品数据(含定时同步)
2. 检测人员编辑样品信息并录入检测结果(检测项目、合格/不合格、指标值)
3. 上传PDF格式检测报告至本地文件服务器
4. 将检测结果和报告URL推送回客户方API
5. 支持多维度查询过滤、PDF报告下载和Excel检测结果导出

## Technical Context

**Language/Version**: Python 3.11+ (后端), Node.js 18+ (前端构建)
**Primary Dependencies**:

- 后端: FastAPI 0.104+, SQLAlchemy 2.0+, Alembic, Pydantic, python-multipart, APScheduler, httpx, openpyxl (Excel导出)
- 前端: Vue 3.3+, Ant Design Vue 4.0+, Vue Router, Pinia, Axios, Vite, xlsx (Excel导出)
- 数据库: PostgreSQL 15+
- 容器: Docker, Docker Compose

**Storage**:

- 结构化数据: PostgreSQL
- 文件存储: 本地文件系统 `/uploads/reports/{year}/{month}/`
- 静态文件服务: FastAPI StaticFiles中间件或Nginx

**Testing**:

- 后端: pytest, pytest-asyncio, pytest-cov, httpx TestClient
- 前端: Vitest, @vue/test-utils, Playwright(E2E可选)
- API测试: Postman/httpx

**Target Platform**:

- 部署: Docker容器(Linux),支持本地开发环境(Windows/macOS/Linux)
- 浏览器: Chrome 90+, Firefox 88+, Edge 90+
- 分辨率: 1366x768及以上

**Project Type**: Web应用(前后端分离)

**Performance Goals**:

- API响应: 简单查询P95<200ms, 复杂查询P95<500ms, 报告生成P95<2s
- 页面加载: FCP<1.5s, LCP<2.5s, FID<100ms
- 并发: 支持10并发用户无性能下降
- 文件上传: 10MB PDF<30秒

**Constraints**:

- 内部网络部署,单客户对接
- 本地文件存储,需监控空间(预警阈值10GB)
- 固定API认证配置(app_id: 689_abc, 密钥: 67868790)
- 定时同步间隔30分钟

**Scale/Scope**:

- 用户规模: ≤10并发用户
- 数据规模: 每月100-500份检测报告,年度存储6-30GB
- 功能模块: 登录认证、数据同步、样品管理、检测录入、报告管理、结果提交、查询过滤、Excel导出

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

根据项目宪章(`.specify/memory/constitution.md`)验证以下合规性:

### 代码质量检查

- [x] 编码规范和命名约定已定义 - Python遵循PEP 8,TypeScript/Vue使用ESLint+Prettier,类名PascalCase,函数/变量camelCase
- [x] 代码审查流程已明确 - 所有PR需至少一人审核,通过CI/CD检查后合并
- [x] 静态分析工具已配置 - Python使用flake8+mypy,前端使用ESLint,圈复杂度限制≤10
- [x] 文档注释标准已确立 - Python使用docstring(Google风格),TypeScript使用JSDoc,公共API必须注释

### 测试标准检查

- [x] TDD 流程已规划(测试先行) - 先编写pytest测试用例(后端)和Vitest测试(前端),测试失败后实现
- [x] 测试覆盖率目标:≥ 80%(关键逻辑 100%) - 使用pytest-cov和Vitest覆盖率报告监控,API调用/文件上传/数据提交=100%
- [x] 测试分层策略已定义(单元/集成/端到端) - 单元测试(models/services),契约测试(API端点),集成测试(数据库/外部API)
- [x] 测试数据准备计划已制定 - 使用pytest fixtures创建测试数据库,mock客户方API响应,准备样例PDF文件

### 用户体验检查

- [x] UI/UX 设计系统已建立或引用 - 使用Ant Design Vue组件库,确保视觉和交互一致性
- [x] 可访问性标准已包含(WCAG 2.1 AA) - 表单字段必须有label,支持键盘导航,错误提示清晰,色盲友好配色
- [x] 交互一致性规范已定义 - 删除操作二次确认,加载状态统一显示,表单验证错误位置一致
- [x] 用户反馈机制已设计 - 操作反馈<200ms(按钮loading状态),长操作显示进度条,错误消息明确+重试选项

### 性能要求检查

- [x] 性能基准已明确(响应时间、并发能力) - 详见Performance Goals,API响应/页面加载/并发用户均有明确指标
- [x] 性能监控方案已规划 - 使用FastAPI middleware记录响应时间,PostgreSQL慢查询日志(>500ms告警)
- [x] 可扩展性架构已考虑 - 无状态API设计(支持水平扩展),数据库索引优化,缓存策略(可选)
- [x] 资源限制已识别(内存、查询数量等) - 单API请求<256MB,查询分页50条/页,文件上传<10MB,存储空间监控

**✅ 宪章合规性验证通过 - 所有检查点均已满足,无违规项需要说明**

## Project Structure

### Documentation (this feature)

```text
specs/1-food-quality-system/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (development guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── examples/        # Request/response examples
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                   # FastAPI application entry
│   ├── config.py                 # Configuration management (env vars)
│   ├── database.py               # SQLAlchemy session/engine setup
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── check_object.py       # CheckObject model
│   │   ├── check_item.py         # CheckObjectItem/CheckItem models
│   │   ├── sync_log.py           # SyncLog model
│   │   └── system_config.py      # SystemConfig model
│   ├── schemas/                  # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── check_object.py
│   │   ├── check_result.py
│   │   └── sync_log.py
│   ├── api/                      # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependencies (auth, db session)
│   │   ├── auth.py               # Login/logout endpoints
│   │   ├── check_objects.py      # Sample CRUD endpoints
│   │   ├── sync.py               # Data sync endpoints
│   │   ├── reports.py            # Report upload/download
│   │   └── submit.py             # Submit results to client API
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── client_api_service.py # Client API integration
│   │   ├── sync_service.py       # Data synchronization
│   │   ├── file_service.py       # File upload/storage
│   │   └── submit_service.py     # Result submission
│   ├── tasks/                    # Background tasks
│   │   ├── __init__.py
│   │   └── scheduler.py          # APScheduler setup (30min sync)
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── security.py           # Password hash, MD5 sign
│   │   ├── pagination.py         # Pagination helper
│   │   └── storage.py            # Disk space monitoring
│   └── middleware/
│       ├── __init__.py
│       └── performance.py        # Response time logging
├── alembic/                      # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/                     # Unit tests
│   │   ├── test_models.py
│   │   ├── test_schemas.py
│   │   └── test_services.py
│   ├── contract/                 # API contract tests
│   │   ├── test_auth_api.py
│   │   ├── test_check_api.py
│   │   └── test_sync_api.py
│   └── integration/              # Integration tests
│       ├── test_client_api.py    # Mock client API calls
│       └── test_file_upload.py
├── uploads/                      # Local file storage
│   └── reports/
│       ├── 2025/
│       └── .gitkeep
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Backend container
└── .env.example                  # Environment variables template

frontend/
├── src/
│   ├── main.ts                   # Vue app entry
│   ├── App.vue                   # Root component
│   ├── router/
│   │   └── index.ts              # Vue Router configuration
│   ├── stores/                   # Pinia stores
│   │   ├── user.ts               # User/auth state
│   │   └── checkObject.ts        # Check object state
│   ├── views/                    # Page components
│   │   ├── LoginView.vue         # Login page
│   │   ├── DashboardView.vue     # Sample list page
│   │   ├── CheckDetailView.vue   # Sample detail/edit page
│   │   └── ReportManageView.vue  # Report management page
│   ├── components/               # Reusable components
│   │   ├── DataSyncButton.vue    # "Get Data" button
│   │   ├── CheckResultForm.vue   # Result input form
│   │   ├── ReportUpload.vue      # PDF upload component
│   │   ├── QueryFilter.vue       # Multi-dimension filter
│   │   └── PaginationTable.vue   # Paginated table
│   ├── services/                 # API client
│   │   ├── api.ts                # Axios instance
│   │   ├── authService.ts        # Auth API calls
│   │   ├── checkService.ts       # Check object API calls
│   │   └── syncService.ts        # Sync API calls
│   ├── utils/
│   │   ├── request.ts            # HTTP interceptors
│   │   └── constants.ts          # Constants
│   ├── assets/                   # Static assets
│   └── styles/                   # Global styles
├── tests/
│   ├── unit/                     # Vitest unit tests
│   │   └── components/
│   └── e2e/                      # Playwright E2E (optional)
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── Dockerfile                    # Frontend container
└── .env.example

docker-compose.yml                # Orchestrate backend+frontend+PostgreSQL
.dockerignore
.gitignore
README.md                         # Project overview and setup
```

**Structure Decision**: 采用Web应用架构(Option 2),前后端分离:

- `backend/`: Python FastAPI后端,提供RESTful API,处理业务逻辑、数据库操作、文件存储、外部API集成
- `frontend/`: Vue 3前端,提供用户界面,调用后端API,使用Ant Design Vue组件
- `docker-compose.yml`: 统一管理3个容器(backend, frontend, PostgreSQL),简化部署

## Complexity Tracking

**无需填写** - Constitution Check 已通过,无违规项需要说明。

---

## Phase 0: Research & Technology Decisions

*待生成 - 将创建 research.md 文档*

## Phase 1: Design Artifacts

*待生成 - 将创建以下文档:*

- data-model.md: 数据库表结构和关系
- contracts/openapi.yaml: API契约定义
- quickstart.md: 开发环境快速启动指南
