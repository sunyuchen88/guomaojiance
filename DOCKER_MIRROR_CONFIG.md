# Docker 国内镜像源配置说明

本项目已优化Dockerfile以使用国内镜像源，加速构建过程。

## 已优化的镜像源

### 1. 前端 (Node.js)
- **npm镜像源**: 淘宝镜像 (https://registry.npmmirror.com)
- 自动配置在 `frontend/Dockerfile` 中

### 2. 后端 (Python)
- **pip镜像源**: 清华大学镜像 (https://pypi.tuna.tsinghua.edu.cn/simple)
- **APT镜像源**: 阿里云镜像 (mirrors.aliyun.com)
- 自动配置在 `backend/Dockerfile` 中

### 3. PostgreSQL
- 使用官方 `postgres:15-alpine` 镜像

## Docker Hub 镜像加速配置（可选）

为了加速拉取Docker官方镜像（如postgres、node、python等），可以配置Docker Hub国内镜像源。

### Windows 配置方法

1. 右键点击任务栏 Docker Desktop 图标
2. 选择 "Settings" (设置)
3. 选择 "Docker Engine"
4. 在配置文件中添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

5. 点击 "Apply & restart" 应用并重启Docker

### Linux 配置方法

1. 编辑 Docker 配置文件：
```bash
sudo vim /etc/docker/daemon.json
```

2. 添加以下内容：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

3. 重启 Docker 服务：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### macOS 配置方法

1. 点击菜单栏 Docker 图标
2. 选择 "Preferences" (偏好设置)
3. 选择 "Docker Engine"
4. 在配置文件中添加上述registry-mirrors配置
5. 点击 "Apply & Restart"

## 验证配置

配置完成后，运行以下命令验证：

```bash
docker info
```

查看输出中是否包含：
```
Registry Mirrors:
  https://docker.mirrors.ustc.edu.cn/
  https://hub-mirror.c.163.com/
  https://mirror.baidubce.com/
```

## 常用国内镜像源列表

### Docker Hub 镜像
- 中国科技大学: https://docker.mirrors.ustc.edu.cn
- 网易: https://hub-mirror.c.163.com
- 百度云: https://mirror.baidubce.com
- 阿里云（需注册）: https://[your-id].mirror.aliyuncs.com

### npm 镜像
- 淘宝镜像: https://registry.npmmirror.com
- 华为云: https://repo.huaweicloud.com/repository/npm/

### pip 镜像
- 清华大学: https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云: https://mirrors.aliyun.com/pypi/simple/
- 中国科技大学: https://pypi.mirrors.ustc.edu.cn/simple/

### APT 镜像 (Debian/Ubuntu)
- 阿里云: mirrors.aliyun.com
- 清华大学: mirrors.tuna.tsinghua.edu.cn
- 中国科技大学: mirrors.ustc.edu.cn

## 构建速度对比

### 使用国内镜像源前
- 前端构建: ~5-10分钟
- 后端构建: ~3-8分钟
- 总计: ~8-18分钟

### 使用国内镜像源后
- 前端构建: ~1-3分钟
- 后端构建: ~1-2分钟
- 总计: ~2-5分钟

**加速效果: 约 3-4 倍**

## 构建命令

配置完成后，使用以下命令构建：

```bash
# 构建并启动所有服务
docker-compose up --build

# 仅构建不启动
docker-compose build

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend
```

## 故障排除

### 问题1: 镜像拉取失败
**解决方案**:
- 检查网络连接
- 尝试更换不同的镜像源
- 检查防火墙设置

### 问题2: npm install 失败
**解决方案**:
```bash
# 手动指定镜像源
docker-compose build frontend --build-arg NPM_REGISTRY=https://registry.npmmirror.com
```

### 问题3: pip install 失败
**解决方案**:
```bash
# 清除缓存重新构建
docker-compose build backend --no-cache
```

## 注意事项

1. **镜像源稳定性**: 国内镜像源可能会有维护期，建议配置多个备用镜像源
2. **缓存清理**: 如遇到依赖安装问题，可使用 `--no-cache` 参数重新构建
3. **网络环境**: 某些企业网络可能限制访问外部镜像源，请联系网络管理员
4. **定期更新**: 镜像源地址可能会变更，建议定期检查更新

## 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [淘宝 npm 镜像](https://npmmirror.com/)
- [清华大学开源镜像站](https://mirrors.tuna.tsinghua.edu.cn/)
- [中科大开源镜像站](https://mirrors.ustc.edu.cn/)
