# Quickstart Guide: 食品质检系统

**Feature**: 食品质检系统
**Date**: 2025-11-19
**Audience**: 开发人员

## Prerequisites

- Docker Desktop 4.20+ (Windows/macOS) 或 Docker Engine 24+ (Linux)
- Git 2.30+
- (可选) Python 3.11+, Node.js 18+, PostgreSQL 15+ (本地开发)

## Quick Start (Docker Compose)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd 检测系统
git checkout 1-food-quality-system

# 复制环境变量模板
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 编辑backend/.env,设置必要配置
nano backend/.env
```

**backend/.env示例**:
```env
DATABASE_URL=postgresql://admin:password@db:5432/food_quality
SECRET_KEY=your-secret-key-change-in-production
CLIENT_APP_ID=689_abc
CLIENT_SECRET=67868790
CLIENT_API_BASE_URL=https://test1.yunxianpei.com
SERVER_DOMAIN=http://localhost:8000
SYNC_INTERVAL_MINUTES=30
```

### 2. Start All Services

```bash
# 启动backend + frontend + PostgreSQL
docker-compose up -d

# 查看日志
docker-compose logs -f

# 等待服务启动(约30秒)
```

### 3. Initialize Database

```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# (可选) 插入测试数据
docker-compose exec backend python scripts/seed_data.py
```

### 4. Access Application

- **前端**: http://localhost (Vue 3 UI)
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs (Swagger UI)
- **数据库**: localhost:5432 (用户名:admin, 密码见.env)

**默认登录账号**:
- 用户名: `admin`
- 密码: `admin123`

### 5. Verify Setup

```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 测试登录API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 前端访问
open http://localhost
```

---

## Local Development (No Docker)

### Backend Setup

```bash
cd backend

# 创建Python虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动PostgreSQL(本地或Docker)
docker run -d --name postgres \
  -e POSTGRES_DB=food_quality \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# 运行迁移
alembic upgrade head

# 启动开发服务器(热重载)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器(热重载)
npm run dev

# 访问: http://localhost:5173
```

---

## Development Workflow

### 1. Create New API Endpoint

```python
# backend/app/api/example.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/")
async def get_examples(user=Depends(get_current_user)):
    return {"message": "Hello from example endpoint"}
```

注册路由:
```python
# backend/app/main.py
from app.api import example

app.include_router(example.router, prefix="/api/v1")
```

### 2. Create New Vue Component

```vue
<!-- frontend/src/components/ExampleComponent.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'

const loading = ref(false)

const handleClick = async () => {
  loading.value = true
  try {
    // Call API
    message.success('操作成功')
  } catch (error) {
    message.error('操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <a-button :loading="loading" @click="handleClick">
    点击测试
  </a-button>
</template>
```

### 3. Run Tests

```bash
# 后端测试
cd backend
pytest -v --cov=app --cov-report=html

# 前端测试
cd frontend
npm run test

# E2E测试(可选)
npm run test:e2e
```

### 4. Database Migration

```bash
cd backend

# 创建新迁移
alembic revision --autogenerate -m "Add new table"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

---

## Troubleshooting

### Port Already in Use

```bash
# 查找占用端口的进程
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 停止占用进程或修改docker-compose.yml端口映射
```

### Database Connection Error

```bash
# 检查PostgreSQL是否运行
docker-compose ps

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### Frontend Build Error

```bash
# 清除node_modules并重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Production Deployment

### 1. Build Images

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 推送到镜像仓库
docker tag food-quality-backend:latest your-registry/food-quality-backend:1.0.0
docker push your-registry/food-quality-backend:1.0.0
```

### 2. Deploy to Server

```bash
# SSH到生产服务器
ssh user@production-server

# 拉取镜像并启动
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 运行迁移
docker-compose exec backend alembic upgrade head
```

### 3. Configure Nginx (可选)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /reports/ {
        alias /path/to/uploads/reports/;
    }
}
```

---

## Useful Commands

```bash
# Docker管理
docker-compose ps              # 查看运行状态
docker-compose logs -f         # 实时日志
docker-compose down            # 停止并删除容器
docker-compose down -v         # 删除容器+数据卷

# 数据库管理
docker-compose exec db psql -U admin -d food_quality  # 进入PostgreSQL
docker-compose exec backend alembic current           # 查看当前迁移版本

# 代码质量检查
cd backend && flake8 app/      # Python linting
cd backend && mypy app/        # Type checking
cd frontend && npm run lint    # TypeScript/Vue linting
```

---

## Next Steps

1. 阅读 [API文档](./contracts/api-summary.md)
2. 查看 [数据模型](./data-model.md)
3. 运行 `/speckit.tasks` 生成实施任务列表
4. 开始TDD开发流程(先写测试!)

**Happy Coding! 🚀**
