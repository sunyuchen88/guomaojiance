# 生产环境部署指南

本文档说明如何将食品质检系统部署到生产服务器 **jiance.wxhzch.com**。

## 环境信息

- **生产域名**: jiance.wxhzch.com
- **前端**: https://jiance.wxhzch.com (端口 80)
- **后端API**: https://jiance.wxhzch.com/api/v1 (端口 8000)
- **数据库**: PostgreSQL 15 (端口 5432)

## 前置要求

### 服务器要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+ 或 CentOS 7+)
- **内存**: 至少 2GB RAM
- **磁盘**: 至少 20GB 可用空间
- **网络**: 公网IP，域名已解析到服务器

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- SSL证书 (用于HTTPS)

## 部署步骤

### 1. 安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 上传项目文件

```bash
# 在服务器上创建项目目录
mkdir -p /opt/food-quality-system
cd /opt/food-quality-system

# 上传项目文件（使用scp、rsync或git）
# 方法1: 使用git
git clone <your-repository-url> .

# 方法2: 使用rsync从本地上传
# rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
#   /local/path/to/project/ user@jiance.wxhzch.com:/opt/food-quality-system/
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.prod.example .env

# 编辑环境变量
nano .env
```

**重要配置项**:
```bash
# 数据库密码（必须修改）
POSTGRES_PASSWORD=your-strong-password-here

# JWT密钥（必须修改为随机字符串）
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# 客户端API配置
API_BASE_URL=https://test1.yunxianpei.com
CLIENT_APP_ID=689_abc
CLIENT_SECRET=67868790
```

生成强密码命令：
```bash
# 生成随机JWT密钥
openssl rand -hex 32

# 生成随机数据库密码
openssl rand -base64 24
```

### 4. 配置SSL证书（HTTPS）

#### 方法1: 使用Let's Encrypt（推荐）

```bash
# 安装certbot
sudo apt-get update
sudo apt-get install -y certbot

# 停止前端容器以释放80端口
docker-compose -f docker-compose.prod.yml stop frontend

# 申请SSL证书
sudo certbot certonly --standalone -d jiance.wxhzch.com

# 证书将保存在: /etc/letsencrypt/live/jiance.wxhzch.com/
```

#### 方法2: 使用已有证书

将证书文件放置到项目目录：
```bash
mkdir -p ssl
cp /path/to/your/cert.pem ssl/
cp /path/to/your/key.pem ssl/
```

### 5. 更新Nginx配置支持HTTPS

编辑 `frontend/nginx.conf`，添加HTTPS配置：

```nginx
server {
    listen 80;
    server_name jiance.wxhzch.com;

    # HTTP自动跳转HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jiance.wxhzch.com;

    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置保持不变
    # ...
}
```

更新 `docker-compose.prod.yml` 的前端服务：

```yaml
  frontend:
    # ...
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt/live/jiance.wxhzch.com:/etc/nginx/ssl:ro
    # ...
```

### 6. 启动服务

```bash
# 构建并启动所有服务
docker-compose -f docker-compose.prod.yml up -d --build
```

首次构建时间约2-5分钟（已优化国内镜像源）。

### 7. 初始化数据库

```bash
# 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 8. 验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 测试后端API
curl https://jiance.wxhzch.com/api/v1/health

# 访问前端
# 浏览器打开: https://jiance.wxhzch.com
```

**默认登录信息**:
- 账号: `admin`
- 密码: `admin123`

⚠️ **重要**: 首次登录后请立即修改管理员密码！

## 本地开发环境

本地开发环境使用 `docker-compose.yml`（不是 `docker-compose.prod.yml`）：

```bash
# 本地开发环境启动
docker-compose up -d

# 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

## 域名配置说明

### 生产环境 (jiance.wxhzch.com)
- **前端URL**: https://jiance.wxhzch.com
- **后端API**: https://jiance.wxhzch.com/api/v1
- **CORS配置**: 已自动配置支持该域名

### 本地开发环境
- **前端URL**: http://localhost:3000
- **后端API**: http://localhost:8000/api/v1
- **CORS配置**: 已自动配置支持 localhost

## 常用运维命令

### 查看服务状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 更新代码并重新部署
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 运行数据库迁移（如有需要）
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 停止服务
```bash
# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 停止并删除数据卷（谨慎使用！）
docker-compose -f docker-compose.prod.yml down -v
```

### 备份数据库
```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres food_quality > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复数据库
```bash
# 恢复数据库
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres food_quality < backups/backup_20231201_120000.sql
```

## 性能优化建议

### 1. 数据库优化
```bash
# 编辑 docker-compose.prod.yml，添加PostgreSQL优化配置
services:
  postgres:
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "max_connections=200"
```

### 2. 日志轮转
配置Docker日志大小限制：

编辑 `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

重启Docker:
```bash
sudo systemctl restart docker
```

### 3. 定期清理
```bash
# 清理未使用的Docker镜像
docker system prune -a

# 清理未使用的卷
docker volume prune
```

## 监控和告警

### 健康检查
```bash
# 后端健康检查
curl https://jiance.wxhzch.com/api/v1/health

# 前端健康检查
curl https://jiance.wxhzch.com/health
```

### 推荐监控工具
- **Prometheus + Grafana**: 系统监控
- **Sentry**: 错误追踪
- **Uptime Kuma**: 服务可用性监控

## 安全建议

1. **修改默认密码**: 数据库密码、JWT密钥、管理员密码
2. **配置防火墙**: 只开放必要端口 (80, 443, 22)
3. **启用SSL/TLS**: 强制HTTPS访问
4. **定期更新**: 系统补丁和Docker镜像
5. **日志审计**: 定期检查访问日志和错误日志
6. **数据备份**: 每日自动备份数据库

## 故障排查

### 问题1: 跨域错误
**症状**: 前端无法访问后端API，浏览器控制台显示CORS错误

**解决方案**:
1. 确认 `docker-compose.prod.yml` 中的 `ALLOWED_ORIGINS` 包含正确的域名
2. 确认前端构建时的 `VITE_API_BASE_URL` 正确
3. 重新构建服务: `docker-compose -f docker-compose.prod.yml up -d --build`

### 问题2: 无法访问网站
**检查清单**:
- [ ] 域名DNS解析是否正确
- [ ] 防火墙是否开放80/443端口
- [ ] Docker容器是否正常运行
- [ ] Nginx配置是否正确
- [ ] SSL证书是否有效

### 问题3: 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose -f docker-compose.prod.yml logs postgres

# 检查数据库连接
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d food_quality -c "SELECT 1;"
```

## 技术支持

如遇到问题，请提供以下信息：
1. 错误信息或截图
2. 相关日志
3. 服务状态
4. 环境信息

---

**部署完成后请删除本文档中的敏感信息示例，确保生产环境安全！**
