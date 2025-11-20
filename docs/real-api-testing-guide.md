# 真实接口切换测试指南

**切换日期**: 2025-11-20
**配置变更**: USE_MOCK_CLIENT_API: false

## ✅ 已完成配置

### 环境变量配置
```yaml
API_BASE_URL: https://test1.yunxianpei.com
CLIENT_APP_ID: 689_abc
CLIENT_SECRET: 67868790
USE_MOCK_CLIENT_API: false  # 已切换到真实接口
```

### 接口端点
1. **数据获取接口**: `/admin/api/test/check/data`
   - 用途: 从客户方拉取待检测样品数据
   - 方法: POST (form-urlencoded)
   - 签名算法: MD5(app_id & random_str & time & key)

2. **结果提交接口**: `/admin/api/test/check/feedback`
   - 用途: 提交检测结果到客户方
   - 方法: POST (form-urlencoded)

## 📋 测试步骤

### 1. 验证服务状态
```bash
# 检查所有容器状态
docker-compose -p food-quality ps

# 检查后端环境变量
docker-compose -p food-quality exec backend printenv | grep USE_MOCK
# 应该显示: USE_MOCK_CLIENT_API=false
```

### 2. 测试数据同步功能

#### 方式一：通过前端界面测试
1. 打开浏览器访问 `http://localhost:3000`
2. 登录系统（用户名: admin, 密码: admin123）
3. 在首页点击 **"获取数据"** 按钮
4. 观察数据是否从真实接口拉取

**预期结果**:
- ✅ 显示"正在同步数据..."提示
- ✅ 如果成功，显示"数据同步成功"
- ✅ 表格中显示从客户方获取的真实数据
- ❌ 如果失败，显示具体错误信息

#### 方式二：通过API直接测试
```bash
# 1. 先登录获取token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 复制返回的access_token

# 3. 调用同步接口
curl -X POST http://localhost:8000/api/v1/sync/fetch \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 查看后端日志

实时查看同步日志：
```bash
docker-compose -p food-quality logs backend -f
```

**成功的日志标志**:
```
INFO - Requesting: https://test1.yunxianpei.com/admin/api/test/check/data
INFO - API Response status: 200
INFO - Fetched X check objects from client API
```

**失败的日志标志**:
```
ERROR - Failed to fetch from client API: [错误详情]
```

### 4. 检查数据库

验证数据是否正确存储：
```bash
# 连接到数据库
docker-compose -p food-quality exec postgres psql -U postgres -d food_quality

# 查询同步日志
SELECT id, sync_type, status, fetched_count, start_time, error_message
FROM sync_logs
ORDER BY start_time DESC
LIMIT 5;

# 查询检测对象数量
SELECT COUNT(*) FROM check_objects;

# 查看最新的检测对象
SELECT id, check_object_union_num, submission_goods_name, submission_person_company, status
FROM check_objects
ORDER BY create_time DESC
LIMIT 10;

# 退出
\q
```

## 🔍 故障排查

### 问题1: 连接超时
**现象**:
```
ERROR - Failed to fetch: TimeoutException
```

**原因**:
- 网络连接问题
- 客户方API服务器无法访问

**解决方案**:
```bash
# 测试网络连接
curl -I https://test1.yunxianpei.com

# 检查DNS解析
nslookup test1.yunxianpei.com
```

### 问题2: 签名验证失败
**现象**:
```
API Response status: 401
或
"msg": "签名验证失败"
```

**原因**:
- CLIENT_APP_ID 或 CLIENT_SECRET 配置错误
- 签名算法实现错误

**解决方案**:
1. 验证配置:
```bash
docker-compose -p food-quality exec backend printenv | grep CLIENT
```

2. 检查签名算法实现:
```python
# 查看 backend/app/services/client_api_service.py
# _generate_signature 方法
```

### 问题3: 返回HTML而非JSON
**现象**:
```
ERROR - JSONDecodeError: Expecting value
LOG - API Response text: <!DOCTYPE html>...
```

**原因**:
- 接口端点错误
- 客户方API返回错误页面

**解决方案**:
1. 检查端点配置是否正确
2. 查看完整响应内容确认错误原因:
```bash
docker-compose -p food-quality logs backend | grep "API Response text"
```

### 问题4: 数据格式不匹配
**现象**:
```
ERROR - KeyError: 'check_object_id'
或
ERROR - Unexpected response format
```

**原因**:
- 客户方API返回的数据格式与预期不符

**解决方案**:
1. 查看实际返回的数据结构
2. 更新 `backend/app/services/sync_service.py` 的字段映射

## 📊 监控指标

### 成功指标
- ✅ 同步日志状态为 "success"
- ✅ fetched_count > 0
- ✅ error_message 为空
- ✅ check_objects 表中有新数据
- ✅ 前端界面能正常显示数据

### 失败指标
- ❌ 同步日志状态为 "failed"
- ❌ error_message 有内容
- ❌ 后端日志显示HTTP错误（4xx, 5xx）

## 🔄 回滚到Mock模式

如果真实接口调用失败，可以快速回滚：

```bash
# 1. 修改配置
# 编辑 docker-compose.yml，将 USE_MOCK_CLIENT_API 改为 "true"

# 2. 重新创建容器
docker-compose -p food-quality up -d --force-recreate backend

# 3. 验证
docker-compose -p food-quality exec backend printenv | grep USE_MOCK
# 应显示: USE_MOCK_CLIENT_API=true
```

## 📞 技术支持

如遇到问题，请收集以下信息：

1. **后端日志**:
```bash
docker-compose -p food-quality logs backend --tail 100 > backend_logs.txt
```

2. **同步日志**:
```sql
SELECT * FROM sync_logs ORDER BY start_time DESC LIMIT 10;
```

3. **环境变量**:
```bash
docker-compose -p food-quality exec backend printenv > env_vars.txt
```

4. **网络测试**:
```bash
curl -v https://test1.yunxianpei.com/admin/api/test/check/data
```

## 📝 注意事项

1. **数据一致性**:
   - 首次切换到真实接口后，可能会拉取大量历史数据
   - 建议在非高峰期进行切换

2. **性能影响**:
   - 真实API调用比Mock数据慢
   - 首次同步可能需要较长时间

3. **数据安全**:
   - CLIENT_SECRET 是敏感信息，不要泄露
   - 生产环境应使用更安全的密钥管理方案

4. **定时任务**:
   - 系统每30分钟自动同步一次
   - 首次同步建议手动触发，确保配置正确

## ✅ 验收清单

- [ ] 环境变量 USE_MOCK_CLIENT_API=false
- [ ] 服务正常启动，无错误日志
- [ ] 手动触发数据同步成功
- [ ] 数据库中有真实数据
- [ ] 前端界面能正常显示和操作
- [ ] 自动定时同步正常工作
- [ ] 结果提交到客户方成功

完成以上所有检查项后，即可确认真实接口切换成功！
