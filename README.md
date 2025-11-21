# 食品质检系统

国贸食品科学研究院食品质检系统,用于对接客户方系统,实现检测样品数据自动获取、检测结果录入、PDF报告上传、检测结果自动提交和Excel数据导出的完整业务流程。

## 技术栈

### 后端

- **框架**: Python 3.11 + FastAPI 0.104+
- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **迁移工具**: Alembic
- **认证**: JWT (python-jose)
- **任务调度**: APScheduler
- **Excel导出**: openpyxl

### 前端

- **框架**: Vue 3.3+ (Composition API + TypeScript 5.0+)
- **UI组件**: Ant Design Vue 4.0+
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **构建工具**: Vite
- **Excel导出**: xlsx

### 部署

- **容器化**: Docker + Docker Compose
- **Web服务器**: Uvicorn (开发) / Nginx (生产)
- **镜像源优化**: 已内置npm、pip、apt国内镜像源配置

## 快速开始

### 前置要求

- Docker & Docker Compose
- (可选) Python 3.11+ 和 Node.js 18+ 用于本地开发

### 使用 Docker Compose (推荐)

1. **克隆仓库**

```bash
git clone <repository-url>
cd 检测系统
```

2. **配置环境变量**

```bash
# 后端配置
cp backend/.env.example backend/.env

# 前端配置
cp frontend/.env.example frontend/.env
```

编辑 `backend/.env` 修改必要的配置(数据库密码、JWT密钥等)

3. **【可选】配置Docker国内镜像源加速**

> ⚡ **国内用户推荐**: 项目已内置npm和pip国内镜像源配置，构建速度提升约4倍！

**已优化的镜像源：**

- ✅ npm: 淘宝镜像 (自动配置)
- ✅ pip: 清华大学镜像 (自动配置)
- ✅ apt: 阿里云镜像 (自动配置)

**可选优化：配置Docker Hub镜像加速**

为进一步加速Docker基础镜像拉取，可配置Docker Hub国内镜像源。详见 [`DOCKER_MIRROR_CONFIG.md`](./DOCKER_MIRROR_CONFIG.md)

**构建速度对比：**

- 使用国内镜像源前: 8-18分钟

- 使用国内镜像源后: 2-5分钟

- **加速效果: 约4倍** 🚀
4. **启动所有服务**

```bash
docker-compose up -d
```

首次构建时会自动使用国内镜像源，请耐心等待。

5. **运行数据库迁移**

```bash
docker-compose exec backend alembic upgrade head
```

6. **访问应用**
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **默认登录**:
  - 账号: `admin`
  - 密码: `admin123`

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# （可选）配置pip国内镜像源加速
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# （可选）配置npm国内镜像源加速
npm config set registry https://registry.npmmirror.com

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

## 核心功能

### 1. 数据同步 (US1)

- 自动定时同步(每30分钟)从客户方API获取待检测样品数据
- 手动触发数据同步
- 查看同步日志
- 样品列表查询和编辑

### 2. 检测结果录入 (US2)

- 录入检测项目、检测结果(合格/不合格)、检测指标
- 上传PDF格式检测报告(<10MB)
- 样品状态管理(待检测 → 已检测 → 已提交)

### 3. 结果提交 (US3)

- 将完整检测数据提交至客户方API
- 处理成功和失败响应
- 重试机制

### 4. 数据导出 (US4)

- 下载PDF检测报告
- 导出Excel检测结果(8个字段)
- 支持导出选定样品或查询结果(最多1000条)

### 5. 多维度查询 (US5)

- 按状态筛选(待检测/已检测/已提交)
- 按公司名称模糊查询
- 按检测编号精确查询
- 按采样时间范围查询

### 6. 用户认证 (US6)

- 账号密码登录
- JWT令牌认证
- 2小时会话超时

## 项目结构

```
.
├── backend/                # Python FastAPI后端
│   ├── app/
│   │   ├── api/           # API路由处理
│   │   ├── models/        # SQLAlchemy ORM模型
│   │   ├── schemas/       # Pydantic请求/响应模型
│   │   ├── services/      # 业务逻辑服务
│   │   ├── tasks/         # APScheduler后台任务
│   │   ├── utils/         # 工具函数
│   │   ├── middleware/    # 中间件
│   │   └── main.py        # FastAPI应用入口
│   ├── alembic/           # 数据库迁移
│   ├── tests/             # 测试
│   ├── uploads/           # 文件存储
│   ├── Dockerfile         # 后端Docker配置（已优化国内镜像源）
│   └── requirements.txt   # Python依赖
├── frontend/              # Vue 3前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 可复用组件
│   │   ├── stores/        # Pinia状态管理
│   │   ├── services/      # API客户端
│   │   ├── router/        # Vue Router配置
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试
│   ├── Dockerfile         # 前端Docker配置（已优化国内镜像源）
│   └── package.json       # Node.js依赖
├── specs/                 # 规格说明文档
│   └── 1-food-quality-system/
│       ├── spec.md        # 功能规格
│       ├── plan.md        # 实施计划
│       ├── tasks.md       # 任务列表
│       ├── data-model.md  # 数据模型
│       └── contracts/     # API契约
├── docker-compose.yml     # Docker Compose配置
├── DOCKER_MIRROR_CONFIG.md # Docker国内镜像源配置指南
└── README.md             # 本文件
```

## 数据库

### 主要表结构

- **users**: 用户账号信息
- **check_objects**: 检测样品信息
- **check_object_items**: 检测项目明细
- **check_items**: 检测项目基础表
- **sync_logs**: 数据同步日志
- **system_config**: 系统配置

详见 `specs/1-food-quality-system/data-model.md`

## API端点

### 认证

- `POST /api/v1/auth/login` - 登录

### 数据同步

- `POST /api/v1/sync/fetch` - 手动触发同步
- `GET /api/v1/sync/logs` - 获取同步日志

### 检测样品

- `GET /api/v1/check-objects` - 获取样品列表(支持查询过滤)
- `GET /api/v1/check-objects/{id}` - 获取样品详情
- `PUT /api/v1/check-objects/{id}` - 编辑样品信息
- `PUT /api/v1/check-objects/{id}/result` - 录入检测结果

### 报告管理

- `POST /api/v1/reports/upload` - 上传检测报告
- `GET /api/v1/reports/download/{check_no}` - 下载检测报告
- `POST /api/v1/reports/export-excel` - 导出Excel

### 结果提交

- `POST /api/v1/submit/{check_object_id}` - 提交检测结果

完整API文档见 http://localhost:8000/docs

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/contract/test_auth_api.py
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 代码质量

### 后端

```bash
cd backend

# 代码格式化
black app/

# 代码检查
flake8 app/

# 类型检查
mypy app/
```

### 前端

```bash
cd frontend

# 代码格式化
npm run format

# 代码检查
npm run lint
```

## 生产部署

### 生产环境信息

- **生产域名**: jiance.wxhzch.com
- **前端**: https://jiance.wxhzch.com
- **后端API**: https://jiance.wxhzch.com/api/v1

### 快速部署

1. **配置环境变量**

   ```bash
   # 复制生产环境配置文件
   cp .env.prod.example .env

   # 编辑环境变量，修改敏感信息
   nano .env
   ```

   **必须修改的配置**:
   - `POSTGRES_PASSWORD`: 数据库密码
   - `JWT_SECRET_KEY`: JWT密钥

2. **启动服务**

   ```bash
   # 使用生产配置启动
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

   首次构建约2-5分钟（已优化国内镜像源）。

3. **初始化数据库**

   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

4. **配置SSL证书**（推荐）

   使用Let's Encrypt申请免费SSL证书：
   ```bash
   sudo certbot certonly --standalone -d jiance.wxhzch.com
   ```

5. **访问系统**

   - 前端: https://jiance.wxhzch.com
   - 后端API文档: https://jiance.wxhzch.com/api/v1/docs
   - 默认账号: `admin` / `admin123`

### 环境配置说明

#### 本地开发环境
- 配置文件: `docker-compose.yml`
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- CORS: 已配置支持 localhost

#### 生产环境
- 配置文件: `docker-compose.prod.yml`
- 前端: https://jiance.wxhzch.com
- 后端: https://jiance.wxhzch.com/api/v1
- CORS: 已配置支持 jiance.wxhzch.com

### 详细部署文档

完整的生产环境部署指南（包括SSL配置、监控、备份等）请查看：

📖 **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 生产环境部署完整指南

### 常用运维命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 备份数据库
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres food_quality > backup_$(date +%Y%m%d).sql
```

## 故障排查

### Docker构建速度慢

**问题**: Docker构建过程耗时过长

**解决方案**:

1. 项目已内置npm、pip、apt国内镜像源，自动加速
2. 可选：配置Docker Hub镜像加速，详见 [`DOCKER_MIRROR_CONFIG.md`](./DOCKER_MIRROR_CONFIG.md)
3. 使用 `--no-cache` 重新构建：`docker-compose build --no-cache`

### 依赖安装失败

**问题**: npm install 或 pip install 失败

**解决方案**:

1. 检查网络连接
2. 清除Docker缓存重新构建：
   
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```
3. 如果国内镜像源不可用，可修改 Dockerfile 更换其他镜像源：
   - npm: 可改用华为云镜像 `https://repo.huaweicloud.com/repository/npm/`
   - pip: 可改用阿里云镜像 `https://mirrors.aliyun.com/pypi/simple/`

### 数据库连接失败

- 确认PostgreSQL服务已启动: `docker-compose ps`
- 检查数据库配置: `backend/.env` 中的 `DATABASE_URL`
- 查看日志: `docker-compose logs postgres`

### 前端无法连接后端API

- 确认后端服务已启动: http://localhost:8000/docs
- 检查API基础URL: `frontend/.env` 中的 `VITE_API_BASE_URL`
- 检查CORS配置: `backend/app/main.py` 中的 `ALLOWED_ORIGINS`

### 文件上传失败

- 确认 `backend/uploads/reports` 目录存在且有写权限
- 检查文件大小限制(默认10MB)
- 查看后端日志: `docker-compose logs backend`

## 许可证

[待定]

## 联系方式

[待定]
