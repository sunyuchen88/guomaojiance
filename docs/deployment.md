# 部署指南

本指南介绍如何在生产环境中部署食品质检系统。

---

## 系统要求

### 硬件要求
- **CPU**: 2核心或以上
- **内存**: 4GB RAM 或以上
- **磁盘**: 20GB 可用空间（用于应用和数据库）

### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+ 推荐) 或 Windows Server
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.0+

---

## 快速部署 (Docker Compose)

### 1. 克隆代码仓库

```bash
git clone <repository-url>
cd 检测系统
```

### 2. 配置环境变量

复制示例环境文件：

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，配置以下关键参数：

```env
# 数据库配置
POSTGRES_USER=检测系统_user
POSTGRES_PASSWORD=<strong-password>  # 修改为强密码
POSTGRES_DB=检测系统_db
DATABASE_URL=postgresql://检测系统_user:<strong-password>@db:5432/检测系统_db

# JWT 密钥 (生成随机密钥)
SECRET_KEY=<generate-random-secret-key>

# 客户 API 配置
CLIENT_API_BASE_URL=https://client-api.example.com
CLIENT_API_APP_ID=your_app_id
CLIENT_API_SECRET=your_api_secret

# 应用配置
ALLOWED_ORIGINS=http://localhost:3000,http://your-domain.com
```

**生成随机密钥**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 构建并启动服务

```bash
docker-compose build
docker-compose up -d
```

这将启动以下服务：
- **backend**: FastAPI 后端 (端口 8000)
- **frontend**: Vue.js 前端 (端口 3000)
- **db**: PostgreSQL 数据库 (端口 5432)

### 4. 运行数据库迁移

```bash
docker-compose exec backend alembic upgrade head
```

### 5. 创建初始用户

```bash
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = User(
    username='admin',
    name='管理员',
    email='admin@example.com',
    hashed_password=get_password_hash('admin123')
)
db.add(user)
db.commit()
print('Admin user created: username=admin, password=admin123')
"
```

**重要**: 首次登录后立即修改管理员密码！

### 6. 验证部署

访问以下 URL 验证服务是否正常：

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 生产环境配置

### 使用 Nginx 反向代理

创建 `nginx.conf`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端静态文件
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传大小限制
    client_max_body_size 10M;
}
```

### 配置 HTTPS/SSL

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 数据库备份

创建每日备份 cron 任务：

```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨 2 点备份
0 2 * * * /path/to/backup-script.sh
```

备份脚本示例 (`backup-script.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump -U 检测系统_user 检测系统_db | gzip > $BACKUP_FILE

# 保留最近 30 天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

### 日志管理

配置日志轮转 (`/etc/logrotate.d/检测系统`):

```
/var/log/检测系统/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker-compose restart backend > /dev/null
    endscript
}
```

---

## 环境变量完整列表

### 后端环境变量

```env
# 数据库
POSTGRES_USER=检测系统_user
POSTGRES_PASSWORD=strong_password
POSTGRES_DB=检测系统_db
DATABASE_URL=postgresql://user:pass@db:5432/检测系统_db

# JWT 认证
SECRET_KEY=random_secret_key_32_chars_min
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 客户 API
CLIENT_API_BASE_URL=https://client-api.example.com
CLIENT_API_APP_ID=689_abc
CLIENT_API_SECRET=67868790
CLIENT_API_TIMEOUT=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# 日志
LOG_LEVEL=INFO

# 文件存储
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=10

# 定时任务
SYNC_INTERVAL_MINUTES=30
```

### 前端环境变量

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=食品质检系统
```

---

## 性能优化

### 数据库索引

确保以下索引已创建：

```sql
CREATE INDEX idx_check_object_status ON check_objects(status);
CREATE INDEX idx_check_object_company ON check_objects(company_name);
CREATE INDEX idx_check_object_sampling_time ON check_objects(sampling_time);
CREATE INDEX idx_check_object_created_at ON check_objects(created_at);
```

### 连接池配置

在 `backend/app/database.py` 中配置连接池：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # 连接池大小
    max_overflow=40,   # 最大溢出连接数
    pool_pre_ping=True # 连接前检查
)
```

### 前端构建优化

生产环境构建：

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/`，可使用 Nginx 直接服务静态文件。

---

## 监控与告警

### 健康检查

定期检查服务健康状态：

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
docker-compose exec db pg_isready -U 检测系统_user
```

### 日志监控

查看实时日志：

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 磁盘空间监控

添加到 cron：

```bash
# 每小时检查磁盘空间
0 * * * * /path/to/check-disk-space.sh
```

脚本示例：

```bash
#!/bin/bash
THRESHOLD=90
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "Disk usage is ${USAGE}% - exceeds threshold ${THRESHOLD}%" | \
    mail -s "Disk Space Alert" admin@example.com
fi
```

---

## 故障排查

### 常见问题

**1. 数据库连接失败**
```bash
# 检查数据库是否运行
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

**2. 前端无法连接后端**
```bash
# 检查 CORS 配置
# 确保 ALLOWED_ORIGINS 包含前端域名
```

**3. 文件上传失败**
```bash
# 检查上传目录权限
docker-compose exec backend ls -la /app/uploads

# 检查磁盘空间
df -h
```

**4. 自动同步未运行**
```bash
# 检查 APScheduler 日志
docker-compose logs backend | grep scheduler

# 手动触发同步测试
curl -X POST http://localhost:8000/api/sync/fetch \
  -H "Authorization: Bearer <token>"
```

---

## 升级部署

### 零停机升级

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 备份数据库
./scripts/backup.sh

# 3. 构建新镜像
docker-compose build

# 4. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 5. 重启服务（逐个重启以减少停机时间）
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend
```

---

## 安全建议

1. **定期更新**: 保持 Docker、依赖包更新
2. **强密码**: 使用强密码和密钥
3. **防火墙**: 仅开放必要端口 (80, 443)
4. **SSL/TLS**: 生产环境必须使用 HTTPS
5. **备份**: 每日备份数据库，保留至少 30 天
6. **监控**: 设置日志监控和告警
7. **访问控制**: 限制数据库仅本地访问
8. **密钥管理**: 不要将密钥提交到代码仓库

---

## 联系支持

如有问题，请联系技术支持团队。
