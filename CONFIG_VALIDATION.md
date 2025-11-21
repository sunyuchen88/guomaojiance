# 环境配置验证指南

本文档用于验证本地Docker环境和生产环境(jiance.wxhzch.com)的配置是否正确。

## 配置总览

### ✅ 本地开发环境

| 配置项 | 值 | 配置文件 |
|--------|-----|----------|
| **部署方式** | docker-compose.yml | 根目录 |
| **前端URL** | http://localhost:3000 | - |
| **后端URL** | http://localhost:8000 | - |
| **后端API** | http://localhost:8000/api/v1 | - |
| **数据库** | postgres:5432 (容器内) | docker-compose.yml |
| **CORS允许源** | http://localhost:3000<br>http://localhost<br>http://127.0.0.1:3000<br>http://127.0.0.1 | docker-compose.yml:47 |
| **前端API地址** | http://localhost:8000/api/v1 | docker-compose.yml:66 |
| **后端域名** | http://localhost:8000 | docker-compose.yml:46 |

### ✅ 生产环境 (jiance.wxhzch.com)

| 配置项 | 值 | 配置文件 |
|--------|-----|----------|
| **部署方式** | docker-compose.prod.yml | 根目录 |
| **前端URL** | https://jiance.wxhzch.com | - |
| **后端URL** | https://jiance.wxhzch.com | - |
| **后端API** | https://jiance.wxhzch.com/api/v1 | - |
| **数据库** | postgres:5432 (容器内) | docker-compose.prod.yml |
| **CORS允许源** | https://jiance.wxhzch.com<br>http://jiance.wxhzch.com | docker-compose.prod.yml:39 |
| **前端API地址** | https://jiance.wxhzch.com/api/v1 | docker-compose.prod.yml:61 |
| **后端域名** | https://jiance.wxhzch.com | docker-compose.prod.yml:38 |

## 配置文件对比

### 1. Docker Compose配置

#### 本地环境 (`docker-compose.yml`)
```yaml
backend:
  environment:
    SERVER_DOMAIN: http://localhost:8000
    ALLOWED_ORIGINS: http://localhost:3000,http://localhost,http://127.0.0.1:3000,http://127.0.0.1
frontend:
  environment:
    VITE_API_BASE_URL: http://localhost:8000/api/v1
```

#### 生产环境 (`docker-compose.prod.yml`)
```yaml
backend:
  environment:
    SERVER_DOMAIN: https://jiance.wxhzch.com
    ALLOWED_ORIGINS: https://jiance.wxhzch.com,http://jiance.wxhzch.com
frontend:
  build:
    args:
      VITE_API_BASE_URL: https://jiance.wxhzch.com/api/v1
```

### 2. 前端Dockerfile

#### 本地环境 (`frontend/Dockerfile`)
- 开发模式 (Vite dev server)
- 热重载支持
- 端口：3000

#### 生产环境 (`frontend/Dockerfile.prod`)
- 生产构建 (npm run build)
- Nginx静态文件服务
- 端口：80

### 3. 关键差异总结

| 特性 | 本地环境 | 生产环境 |
|------|----------|----------|
| **协议** | HTTP | HTTPS (推荐) |
| **域名** | localhost | jiance.wxhzch.com |
| **前端端口** | 3000 | 80 (HTTP) / 443 (HTTPS) |
| **后端端口** | 8000 | 8000 |
| **前端服务** | Vite Dev Server | Nginx |
| **代码热重载** | ✅ 支持 | ❌ 不支持 |
| **构建方式** | 开发模式 | 生产构建 |
| **数据卷** | postgres_data | postgres_data_prod |
| **容器名** | food-quality-* | food-quality-*-prod |

## 部署验证步骤

### 本地环境验证

#### 1. 启动服务

```bash
# 在项目根目录
docker-compose up -d --build
```

#### 2. 检查服务状态

```bash
# 检查所有容器是否正常运行
docker-compose ps

# 应该看到以下容器都在运行：
# - food-quality-db (postgres)
# - food-quality-backend (backend)
# - food-quality-frontend (frontend)
```

#### 3. 测试后端API

```bash
# 测试健康检查端点
curl http://localhost:8000/health

# 预期输出：
# {"status":"healthy"}

# 测试API文档
curl http://localhost:8000/docs
# 应该返回HTML内容（Swagger UI）
```

#### 4. 测试CORS配置

```bash
# 测试CORS预检请求
curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# 检查响应头中应包含：
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
```

#### 5. 测试前端访问

```bash
# 浏览器访问
open http://localhost:3000

# 或使用curl测试
curl http://localhost:3000
# 应该返回HTML内容
```

#### 6. 测试前端到后端的连接

1. 打开浏览器: http://localhost:3000
2. 打开浏览器开发者工具 (F12)
3. 切换到 Console 标签
4. 尝试登录
5. 检查 Network 标签，确认：
   - API请求地址是 `http://localhost:8000/api/v1/*`
   - 没有CORS错误
   - 请求成功返回数据

#### 7. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 生产环境验证

#### 1. 准备环境变量

```bash
# 复制并编辑环境变量
cp .env.prod.example .env
nano .env

# 必须修改：
# - POSTGRES_PASSWORD
# - JWT_SECRET_KEY
```

#### 2. 启动服务

```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 3. 检查服务状态

```bash
docker-compose -f docker-compose.prod.yml ps

# 应该看到以下容器都在运行：
# - food-quality-db-prod
# - food-quality-backend-prod
# - food-quality-frontend-prod
```

#### 4. 初始化数据库

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### 5. 测试后端API（服务器上）

```bash
# 健康检查
curl http://localhost:8000/health

# 测试CORS（从外部域名访问）
curl -X OPTIONS https://jiance.wxhzch.com/api/v1/auth/login \
  -H "Origin: https://jiance.wxhzch.com" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 检查响应头
```

#### 6. 测试前端访问（公网）

```bash
# 从外部访问
curl https://jiance.wxhzch.com

# 或浏览器访问
open https://jiance.wxhzch.com
```

#### 7. 完整功能测试

1. 浏览器访问: https://jiance.wxhzch.com
2. 打开开发者工具 (F12)
3. 检查Console是否有错误
4. 尝试登录 (admin / admin123)
5. 检查Network标签：
   - API请求地址应为 `https://jiance.wxhzch.com/api/v1/*`
   - 没有CORS错误
   - 请求成功

#### 8. 查看日志

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

## 常见问题诊断

### 问题1: CORS错误

**症状**: 浏览器控制台显示CORS错误
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/...'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**诊断步骤**:

1. 检查后端CORS配置
```bash
# 本地环境
docker-compose exec backend env | grep ALLOWED_ORIGINS

# 生产环境
docker-compose -f docker-compose.prod.yml exec backend env | grep ALLOWED_ORIGINS
```

2. 检查前端API地址配置
```bash
# 本地环境
docker-compose exec frontend env | grep VITE_API_BASE_URL

# 生产环境：查看构建时的参数
docker-compose -f docker-compose.prod.yml config | grep VITE_API_BASE_URL
```

3. 验证配置是否匹配
   - 前端的来源域名必须在后端的ALLOWED_ORIGINS中

**解决方案**:
- 确保 `docker-compose.yml` 或 `docker-compose.prod.yml` 中的ALLOWED_ORIGINS正确
- 重新构建服务: `docker-compose up -d --build`

### 问题2: 前端无法连接后端

**症状**: 前端页面空白或API请求失败

**诊断步骤**:

1. 检查后端是否运行
```bash
curl http://localhost:8000/health
```

2. 检查前端配置的API地址
```bash
# 浏览器Console执行
console.log(import.meta.env.VITE_API_BASE_URL)
```

3. 检查网络请求
   - 打开浏览器开发者工具 → Network
   - 查看API请求的实际URL
   - 检查请求是否成功

**解决方案**:
- 确保前端和后端都在运行
- 验证API地址配置正确
- 检查防火墙设置

### 问题3: 生产环境SSL证书问题

**症状**: 浏览器显示"不安全的连接"

**诊断步骤**:

1. 检查SSL证书
```bash
curl -v https://jiance.wxhzch.com 2>&1 | grep -i ssl
```

2. 检查证书有效期
```bash
echo | openssl s_client -connect jiance.wxhzch.com:443 2>/dev/null | openssl x509 -noout -dates
```

**解决方案**:
- 按照DEPLOYMENT.md配置SSL证书
- 使用Let's Encrypt申请免费证书

### 问题4: 容器无法启动

**症状**: `docker-compose ps` 显示容器Exit或Restarting

**诊断步骤**:

1. 查看容器日志
```bash
docker-compose logs backend
docker-compose logs frontend
```

2. 检查端口占用
```bash
# 检查3000端口
lsof -i :3000

# 检查8000端口
lsof -i :8000

# 检查5432端口
lsof -i :5432
```

**解决方案**:
- 停止占用端口的程序
- 修改docker-compose.yml中的端口映射
- 检查环境变量配置

## 配置检查清单

### 本地环境启动前

- [ ] Docker和Docker Compose已安装
- [ ] 端口3000、8000、5432未被占用
- [ ] 已检查docker-compose.yml配置
- [ ] ALLOWED_ORIGINS包含localhost相关地址

### 生产环境部署前

- [ ] 服务器已安装Docker和Docker Compose
- [ ] 域名jiance.wxhzch.com已解析到服务器IP
- [ ] 已复制并编辑.env文件
- [ ] 已修改敏感信息（数据库密码、JWT密钥）
- [ ] 端口80、443已开放
- [ ] 已检查docker-compose.prod.yml配置
- [ ] ALLOWED_ORIGINS包含jiance.wxhzch.com
- [ ] 前端构建参数VITE_API_BASE_URL正确

### 功能测试清单

- [ ] 前端页面可以访问
- [ ] 用户可以登录
- [ ] API请求无CORS错误
- [ ] 数据可以正常加载
- [ ] 文件上传功能正常
- [ ] 数据同步功能正常
- [ ] 报告下载功能正常

## 配置文件快速参考

### 修改本地环境配置

```bash
# 编辑本地docker-compose
nano docker-compose.yml

# 关键配置位置：
# - 第46行: SERVER_DOMAIN
# - 第47行: ALLOWED_ORIGINS
# - 第66行: VITE_API_BASE_URL
```

### 修改生产环境配置

```bash
# 编辑生产docker-compose
nano docker-compose.prod.yml

# 关键配置位置：
# - 第38行: SERVER_DOMAIN
# - 第39行: ALLOWED_ORIGINS
# - 第61行: VITE_API_BASE_URL (构建参数)

# 编辑环境变量
nano .env
```

## 总结

### ✅ 配置正确性确认

**本地环境**:
- ✅ CORS配置支持 localhost:3000
- ✅ 前端API地址指向 localhost:8000
- ✅ 开发服务器支持热重载
- ✅ 独立数据卷避免冲突

**生产环境**:
- ✅ CORS配置支持 jiance.wxhzch.com
- ✅ 前端API地址指向 jiance.wxhzch.com
- ✅ 生产构建优化性能
- ✅ 独立数据卷确保安全

### 🎯 核心保证

1. **跨域问题已解决**: 两个环境都正确配置了CORS
2. **环境隔离**: 本地和生产使用不同的配置文件和数据卷
3. **配置明确**: 所有关键配置都有明确的文档说明
4. **易于切换**: 通过不同的docker-compose文件轻松切换环境

---

**验证完成后，请保留此文档作为参考和故障排查指南。**
