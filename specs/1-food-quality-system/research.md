# Technology Research: 食品质检系统

**Feature**: 食品质检系统
**Date**: 2025-11-19
**Purpose**: 技术选型调研和最佳实践研究,为实施计划提供决策依据

## 技术栈选型决策

### 后端框架: Python + FastAPI

**Decision**: 使用Python 3.11+ 和 FastAPI 0.104+

**Rationale**:
- **性能优越**: FastAPI基于Starlette和Pydantic,支持异步处理,性能接近Go/Node.js,满足P95<200ms的响应时间要求
- **开发效率高**: 自动生成OpenAPI文档和交互式API测试界面(/docs),减少API文档维护成本
- **类型安全**: Pydantic模型提供请求/响应数据验证和序列化,减少运行时错误
- **异步支持**: 原生async/await,适合处理I/O密集型操作(数据库查询、外部API调用、文件上传)
- **生态丰富**: SQLAlchemy(ORM)、Alembic(数据库迁移)、APScheduler(定时任务)等成熟库
- **团队熟悉度**: Python语法简洁,学习曲线平缓,适合快速开发

**Alternatives Considered**:
- **Django + DRF**: 功能更全面但更重量级,对于本项目(10并发用户)有过度设计之嫌,且DRF配置繁琐
- **Flask**: 更轻量但缺少现代特性(异步支持、自动文档生成),需要更多手动配置
- **Node.js + Express/Nest.js**: 性能好但团队对JavaScript生态不熟悉,且Python在数据处理和科学计算上有优势

---

### 前端框架: Vue 3 + TypeScript

**Decision**: 使用Vue 3.3+ 和 TypeScript 5.0+

**Rationale**:
- **Composition API**: 提供更好的代码组织和逻辑复用,减少组件复杂度
- **响应式系统优化**: Vue 3的Proxy-based响应式系统性能更好,内存占用更低
- **TypeScript支持**: 原生支持TS,提供类型安全和IDE智能提示,减少运行时错误
- **轻量高效**: Vue 3 bundle size小于其他主流框架,加载速度快,满足FCP<1.5s要求
- **学习曲线友好**: 模板语法直观,文档完善,团队容易上手
- **生态成熟**: Vue Router、Pinia(状态管理)、Vite(构建工具)配套完善

**Alternatives Considered**:
- **React**: 生态最丰富但学习曲线陡峭(hooks、JSX),且需要额外选择状态管理方案(Redux/Zustand)
- **Angular**: 功能强大但过于复杂,不适合小型团队,编译速度慢
- **Svelte**: 性能最优但生态相对不成熟,招聘和维护成本高

---

### UI组件库: Ant Design Vue

**Decision**: 使用Ant Design Vue 4.0+

**Rationale**:
- **组件丰富**: 提供70+高质量组件(Table、Form、Upload、DatePicker等),覆盖90%业务需求
- **企业级**: 专为B端管理系统设计,符合检测系统的业务场景
- **视觉一致性**: 设计规范统一,开箱即用,满足宪章"组件复用率≥90%"要求
- **可访问性**: 组件内置WCAG 2.1 AA支持(键盘导航、ARIA标签、焦点管理)
- **TypeScript支持**: 完整的TS类型定义,开发体验好
- **国际化**: 支持中文和多语言,符合国内团队使用习惯
- **文档完善**: 中文文档详细,示例丰富

**Alternatives Considered**:
- **Element Plus**: 组件质量稍弱,部分组件可访问性不足
- **Naive UI**: 新兴库,生态不够成熟,组件数量少
- **Vuetify**: Material Design风格,与Ant Design的企业级设计不符

---

### 数据库: PostgreSQL 15+

**Decision**: 使用PostgreSQL 15.x

**Rationale**:
- **可靠性高**: ACID事务,强一致性,适合检测数据这种关键业务数据
- **性能优秀**: B-tree/GIN索引,支持复杂查询(多维度筛选、时间范围查询),满足P95<500ms要求
- **JSON支持**: 原生JSONB类型,适合存储客户方API返回的嵌套数据(objectItems数组)
- **全文搜索**: 内置中文分词(pg_jieba插件),支持公司名称模糊查询
- **扩展性**: 支持水平扩展(pg_pool、Citus),虽然当前不需要但为未来留有余地
- **开源免费**: 无许可证成本,社区活跃,文档完善
- **SQLAlchemy支持**: Python ORM生态最成熟的数据库之一

**Alternatives Considered**:
- **MySQL**: 性能略逊,JSON支持不如PostgreSQL,事务隔离级别默认较弱
- **SQLite**: 不支持并发写入,不适合10并发用户场景
- **MongoDB**: NoSQL虽然灵活但对于本项目的关系型数据(样品-检测项目-检测结果)不如PostgreSQL直观

---

### 定时任务: APScheduler

**Decision**: 使用APScheduler 3.10+

**Rationale**:
- **Python原生**: 无需额外服务(Celery需要Redis/RabbitMQ),降低架构复杂度
- **轻量级**: 适合简单定时任务(30分钟同步),不需要复杂的分布式任务队列
- **灵活调度**: 支持cron表达式、interval、date触发器,满足定时同步需求
- **集成简单**: 与FastAPI集成方便,使用@app.on_event("startup")启动调度器
- **持久化支持**: 可选SQLAlchemy job store,任务重启后恢复

**Alternatives Considered**:
- **Celery**: 功能强大但过于重量级,需要消息队列(Redis/RabbitMQ),对于单个30分钟定时任务过度设计
- **Cron**: 系统级但需要额外脚本,不易与应用逻辑集成,错误处理不方便

---

### 文件上传和存储

**Decision**: 使用FastAPI的UploadFile + 本地文件系统存储

**Rationale**:
- **简单直接**: 符合spec.md的决策(Q1:A - 本地文件服务器存储)
- **成本低**: 无需云存储服务费用,检测机构内部网络无需CDN
- **FastAPI原生支持**: `UploadFile`基于Starlette,自动处理multipart/form-data,支持流式上传(大文件)
- **路径组织**: `/uploads/reports/{year}/{month}/{质检编号}_{timestamp}.pdf` 便于管理和备份
- **静态文件服务**: FastAPI的StaticFiles或Nginx提供HTTP访问

**Implementation Pattern**:
```python
from fastapi import UploadFile
from pathlib import Path
import aiofiles

async def save_report(file: UploadFile, check_no: str) -> str:
    # 验证PDF格式
    if file.content_type != "application/pdf":
        raise ValueError("Only PDF files are allowed")

    # 验证文件大小(10MB)
    MAX_SIZE = 10 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise ValueError("File size exceeds 10MB limit")

    # 生成存储路径
    now = datetime.now()
    year, month = now.year, now.strftime("%m")
    filename = f"{check_no}_{int(now.timestamp())}.pdf"
    file_path = Path(f"/uploads/reports/{year}/{month}/{filename}")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 异步写入文件
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    # 返回URL
    return f"http://{{server_domain}}/reports/{year}/{month}/{filename}"
```

**Alternatives Considered**:
- **云对象存储(OSS/S3)**: 更可靠但增加成本和复杂度,当前规模不需要
- **数据库BLOB**: PostgreSQL支持但效率低,备份困难,不推荐

---

### Docker容器化部署

**Decision**: 使用Docker + Docker Compose

**Rationale**:
- **环境一致性**: 开发、测试、生产环境完全一致,避免"在我机器上可以运行"问题
- **快速部署**: docker-compose up一键启动全栈(backend+frontend+PostgreSQL)
- **资源隔离**: 容器间资源隔离,避免端口冲突和依赖冲突
- **易于维护**: 版本管理清晰(Dockerfile),回滚方便
- **成本低**: 无需Kubernetes等复杂编排工具,Docker Compose足够

**Docker Compose架构**:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: food_quality
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@db:5432/food_quality
    volumes:
      - ./uploads:/app/uploads  # 持久化报告文件
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"  # Nginx serve Vue build
```

**Alternatives Considered**:
- **传统部署**: 直接在服务器安装Python/Node/PostgreSQL,配置复杂,不易迁移
- **Kubernetes**: 过于复杂,不适合10用户规模的小型系统

---

### 客户方API集成: HTTPX

**Decision**: 使用httpx 0.25+ (异步HTTP客户端)

**Rationale**:
- **异步支持**: 原生async/await,与FastAPI完美集成,避免阻塞
- **HTTP/2支持**: 性能优于requests库
- **类requests API**: 语法简洁,团队容易上手
- **超时控制**: 精细的超时配置,避免客户API慢响应阻塞系统
- **重试机制**: 可集成tenacity库实现自动重试(网络抖动)

**MD5签名实现**:
```python
import httpx
import hashlib
from datetime import datetime

async def call_client_api(biz: dict, app_id: str, secret: str):
    time = int(datetime.now().timestamp())
    random_str = generate_random_string(5)

    # 生成MD5签名
    sign_data = f"{app_id}&time&{random_str}"
    key = hashlib.md5(secret.encode()).hexdigest()
    sign = hashlib.md5(f"{sign_data}{key}".encode()).hexdigest()

    payload = {
        "app_id": app_id,
        "time": time,
        "random_str": random_str,
        "sign": sign,
        "biz": biz
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://test1.yunxianpei.com/admin/api/test/check/data",
            data=payload  # x-www-form-urlencoded
        )
        return response.json()
```

**Alternatives Considered**:
- **requests**: 同步库,会阻塞事件循环,不适合异步FastAPI
- **aiohttp**: 功能强大但API复杂,httpx更简洁

---

### 会话管理和身份认证

**Decision**: JWT (JSON Web Token) + HTTPOnly Cookie

**Rationale**:
- **无状态**: JWT无需服务器端session存储,支持水平扩展
- **安全性**: HTTPOnly Cookie防止XSS攻击,SameSite=Strict防止CSRF
- **过期控制**: JWT exp claim实现2小时超时(FR-020要求)
- **FastAPI集成**: python-jose库提供JWT编解码,OAuth2PasswordBearer依赖注入

**Implementation Pattern**:
```python
from fastapi import Depend, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None or datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(status_code=401, detail="Token expired")
        return get_user_by_username(username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Alternatives Considered**:
- **Session + Cookie**: 需要服务器端存储(Redis),增加复杂度
- **OAuth2**: 对于内部系统过于复杂,不需要第三方登录

---

### 代码质量工具

**Decision**:
- **Python**: flake8 (linting) + mypy (type checking) + black (formatting)
- **TypeScript/Vue**: ESLint + Prettier + Vue ESLint Plugin

**Rationale**:
- **flake8**: 检查PEP 8合规性,捕获常见错误(未使用变量、缩进)
- **mypy**: 静态类型检查,确保Pydantic模型和函数签名正确
- **black**: 自动格式化,统一代码风格,减少code review争议
- **ESLint**: JavaScript/TypeScript标准linter,可配置规则检查圈复杂度(complexity≤10)
- **Prettier**: 自动格式化,与ESLint集成

**VS Code配置**:
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "eslint.validate": ["javascript", "typescript", "vue"]
}
```

---

### 测试框架

**Decision**:
- **后端**: pytest + pytest-asyncio + pytest-cov + httpx TestClient
- **前端**: Vitest + @vue/test-utils

**Rationale**:
- **pytest**: Python事实标准,fixture机制强大,插件丰富
- **pytest-asyncio**: 支持异步测试,测试FastAPI异步endpoint
- **pytest-cov**: 集成coverage.py,生成覆盖率报告(HTML/XML),确保≥80%
- **httpx TestClient**: FastAPI官方推荐,模拟HTTP请求,无需启动真实服务器
- **Vitest**: 比Jest快10倍,原生ESM支持,与Vite无缝集成,API兼容Jest
- **@vue/test-utils**: Vue官方测试工具,支持组件挂载和交互测试

**测试示例**:
```python
# backend/tests/contract/test_auth_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", data={
            "username": "test_user",
            "password": "test_pass"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
```

```typescript
// frontend/tests/unit/components/DataSyncButton.spec.ts
import { mount } from '@vue/test-utils'
import DataSyncButton from '@/components/DataSyncButton.vue'

describe('DataSyncButton', () => {
  it('shows loading state when syncing', async () => {
    const wrapper = mount(DataSyncButton)
    await wrapper.trigger('click')
    expect(wrapper.find('.ant-btn-loading').exists()).toBe(true)
  })
})
```

---

## 最佳实践研究

### FastAPI项目结构最佳实践

**参考**: [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

**核心实践**:
1. **分层架构**: API层(路由) → Service层(业务逻辑) → Model层(数据访问),遵循单一职责原则
2. **依赖注入**: 使用FastAPI的Depends()管理依赖(数据库session、当前用户),便于测试和解耦
3. **Pydantic模型分离**: 区分ORM Model(SQLAlchemy)和Schema(Pydantic),避免ORM对象泄露到API响应
4. **异步全栈**: 数据库查询、外部API调用、文件I/O全部使用async/await,避免阻塞
5. **配置管理**: 使用pydantic.BaseSettings从环境变量加载配置,支持.env文件
6. **错误处理**: 统一HTTPException格式,提供清晰错误信息(符合QUAL-005)

---

### Vue 3 + TypeScript 最佳实践

**参考**: [Vue 3 Style Guide](https://vuejs.org/style-guide/)

**核心实践**:
1. **Composition API优先**: 使用`<script setup>`语法,代码更简洁,性能更好
2. **组合式函数(Composables)**: 提取可复用逻辑(useAuth, usePagination),减少代码重复
3. **Props类型验证**: 使用TypeScript接口定义props,运行时和编译时双重检查
4. **单文件组件命名**: 使用PascalCase,组件文件名与组件名一致
5. **Pinia状态管理**: 替代Vuex,API更简洁,TypeScript支持更好
6. **路由懒加载**: 使用动态import(),减少首屏bundle size

---

### PostgreSQL性能优化

**核心实践**:
1. **索引策略**:
   - 为查询条件创建索引: `check_object(status)`, `check_object(submission_person_company)`, `check_object(check_object_union_num)`
   - 时间范围查询使用B-tree索引: `check_object(check_start_time)`
   - 避免over-indexing(写入性能下降)

2. **分页优化**:
   - 使用LIMIT/OFFSET,避免全表查询
   - 对于大offset,使用keyset pagination(WHERE id > last_id)

3. **慢查询监控**:
   ```sql
   -- 开启慢查询日志
   ALTER SYSTEM SET log_min_duration_statement = 500; -- 500ms
   SELECT pg_reload_conf();
   ```

4. **连接池**: SQLAlchemy配置pool_size=20, max_overflow=10,避免连接耗尽

---

### 安全最佳实践

**核心实践**:
1. **密码存储**: 使用bcrypt哈希(passlib),加盐存储,防止彩虹表攻击
2. **SQL注入防护**: SQLAlchemy ORM自动参数化查询,避免字符串拼接SQL
3. **文件上传防护**:
   - 验证Content-Type和文件扩展名(仅.pdf)
   - 限制文件大小(10MB)
   - 使用UUID或时间戳重命名文件,避免路径遍历攻击
4. **CORS配置**: 仅允许前端域名,生产环境禁用`allow_origins=["*"]`
5. **敏感数据**: API密钥、数据库密码存储在环境变量,不提交到Git(.env加入.gitignore)

---

## 技术决策总结

| 技术领域 | 选型 | 主要原因 |
|---------|------|---------|
| 后端框架 | Python 3.11 + FastAPI 0.104 | 高性能、异步支持、自动文档、类型安全 |
| 前端框架 | Vue 3.3 + TypeScript 5.0 | Composition API、轻量、TS支持、学习曲线友好 |
| UI组件库 | Ant Design Vue 4.0 | 企业级、组件丰富、可访问性、国际化 |
| 数据库 | PostgreSQL 15 | ACID、JSON支持、性能、全文搜索 |
| ORM | SQLAlchemy 2.0 | 成熟、灵活、异步支持 |
| 定时任务 | APScheduler 3.10 | 轻量、Python原生、无需额外服务 |
| HTTP客户端 | httpx 0.25 | 异步、HTTP/2、类requests API |
| 身份认证 | JWT + HTTPOnly Cookie | 无状态、安全、易于实现 |
| 文件存储 | 本地文件系统 + FastAPI StaticFiles | 简单、低成本、符合需求 |
| 容器化 | Docker + Docker Compose | 环境一致、快速部署、资源隔离 |
| 代码质量 | flake8 + mypy + black + ESLint + Prettier | 自动化检查、统一风格、类型安全 |
| 测试框架 | pytest + Vitest | 功能强大、异步支持、覆盖率报告 |

**所有技术选型均符合项目宪章要求,支持TDD流程、代码质量标准和性能基准。**
