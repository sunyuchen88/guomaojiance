# API 文档

## 概述

食品质检系统 API 提供完整的检测样品管理、结果录入、报告上传和数据导出功能。

**基础URL**: `http://localhost:8000/api`

**认证方式**: JWT Bearer Token (通过 HTTPOnly Cookie)

---

## 认证 API

### POST /auth/login

用户登录，获取访问令牌。

**请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "name": "测试用户",
    "email": "test@example.com"
  }
}
```

**错误响应** (401 Unauthorized):
```json
{
  "detail": "用户名或密码错误"
}
```

### POST /auth/logout

用户登出，清除令牌。

**响应** (200 OK):
```json
{
  "message": "已成功登出"
}
```

---

## 数据同步 API

### POST /sync/fetch

手动触发从客户 API 获取检测数据。

**权限**: 需要认证

**响应** (200 OK):
```json
{
  "status": "success",
  "message": "同步成功,获取到 15 条数据",
  "synced_count": 15,
  "sync_time": "2024-01-15T10:30:00"
}
```

### GET /sync/logs

获取同步日志列表。

**权限**: 需要认证

**查询参数**:
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页条数，默认 10

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "sync_type": "manual",
      "status": "success",
      "synced_count": 15,
      "error_message": null,
      "sync_time": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10
}
```

---

## 检测对象 API

### GET /check-objects

获取检测对象列表，支持过滤和分页。

**权限**: 需要认证

**查询参数**:
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页条数，默认 10，最大 100
- `status` (int, 可选): 状态过滤 (0=待检测, 1=已检测, 2=已提交)
- `company` (str, 可选): 公司名称模糊搜索
- `check_no` (str, 可选): 检测编号精确搜索
- `start_date` (date, 可选): 采样开始日期 (YYYY-MM-DD)
- `end_date` (date, 可选): 采样结束日期 (YYYY-MM-DD)

**响应** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "check_no": "2024011500001",
      "sample_name": "牛奶",
      "company_name": "测试乳业有限公司",
      "status": 1,
      "sampling_time": "2024-01-10T09:00:00",
      "check_result": "合格",
      "report_url": "/reports/2024/01/abc123.pdf",
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-15T15:30:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 10
}
```

### GET /check-objects/{id}

获取检测对象详情，包含检测项目。

**权限**: 需要认证

**路径参数**:
- `id` (int): 检测对象 ID

**响应** (200 OK):
```json
{
  "id": 1,
  "check_no": "2024011500001",
  "sample_name": "牛奶",
  "company_name": "测试乳业有限公司",
  "status": 1,
  "check_result": "合格",
  "sampling_time": "2024-01-10T09:00:00",
  "remark": "常规检测",
  "check_items": [
    {
      "id": 1,
      "check_item_name": "蛋白质",
      "check_method": "凯氏定氮法",
      "standard_value": "≥2.9g/100g",
      "check_result": "3.2g/100g",
      "result_indicator": "合格"
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T15:30:00"
}
```

### PUT /check-objects/{id}

更新检测对象基本信息。

**权限**: 需要认证

**请求体**:
```json
{
  "sample_name": "更新后的样品名称",
  "company_name": "更新后的公司名称",
  "remark": "备注信息"
}
```

**响应**: 返回更新后的检测对象详情 (同 GET /check-objects/{id})

### PUT /check-objects/{id}/result

录入检测结果，更新状态为"已检测"。

**权限**: 需要认证

**请求体**:
```json
{
  "check_result": "合格",
  "check_items": [
    {
      "id": 1,
      "check_result": "3.2g/100g",
      "result_indicator": "合格"
    }
  ]
}
```

**响应**: 返回更新后的检测对象详情

**错误响应** (400 Bad Request):
```json
{
  "detail": "已提交的检测对象不能修改结果"
}
```

---

## 报告 API

### POST /reports/upload

上传 PDF 检测报告。

**权限**: 需要认证

**请求体**: multipart/form-data
- `file`: PDF 文件 (最大 10MB)

**响应** (200 OK):
```json
{
  "file_url": "/reports/2024/01/abc123-def456.pdf",
  "filename": "abc123-def456.pdf",
  "message": "文件上传成功"
}
```

**错误响应**:
- 400: 文件格式必须是 PDF
- 400: 文件大小不能超过 10MB
- 400: 文件不能为空

### GET /reports/download/{check_no}

下载检测报告。

**权限**: 需要认证

**路径参数**:
- `check_no` (str): 检测编号

**响应**: PDF 文件流

**错误响应**:
- 404: 检测对象不存在
- 404: 报告文件不存在

### POST /reports/export-excel

导出检测结果到 Excel 文件。

**权限**: 需要认证

**请求体**:
```json
{
  "check_object_ids": [1, 2, 3],
  "status": 1,
  "company": "测试公司",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**注意**: `check_object_ids` 和过滤条件二选一

**响应**: Excel 文件流 (.xlsx)

**错误响应** (400 Bad Request):
```json
{
  "detail": "导出数据超过1000行限制,当前数据量: 1200行"
}
```

---

## 提交 API

### POST /submit/{check_object_id}

提交检测结果到客户 API。

**权限**: 需要认证

**路径参数**:
- `check_object_id` (int): 检测对象 ID

**响应** (200 OK):
```json
{
  "success": true,
  "message": "提交成功",
  "check_object_id": 1
}
```

**错误响应**:
- 400: 状态必须为"已检测" (status=1)
- 400: 客户 API 返回错误信息
- 500: 提交失败（网络错误等）

---

## 状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误或业务逻辑错误
- `401 Unauthorized`: 未认证或令牌无效
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求体验证失败
- `500 Internal Server Error`: 服务器内部错误

---

## 错误响应格式

所有错误响应统一格式：

```json
{
  "detail": "错误描述信息"
}
```

---

## 自动生成文档

FastAPI 提供自动生成的交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

这些文档包含所有 API 端点的详细信息，并支持在线测试。

---

## 客户 API 集成

本系统与客户 API 集成，用于数据获取和结果提交。

**客户 API 基础URL**: 配置在 `.env` 文件中

**认证方式**: MD5 签名
- `app_id`: 应用标识
- `secret`: 应用密钥
- `sign`: MD5(app_id + timestamp + secret)

详见 `backend/app/services/client_api_service.py` 实现。
