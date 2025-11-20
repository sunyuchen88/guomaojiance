# API Contract: 食品质检系统

**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api/v1`
**Authentication**: JWT Bearer Token (除登录接口外所有接口需要)

## Authentication Endpoints

### POST /auth/login
登录获取访问令牌

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "name": "管理员",
    "role": "admin"
  }
}
```

---

## Data Sync Endpoints

### POST /sync/fetch
手动触发数据同步

**Request**:
```json
{
  "start_time": "2025-11-18 15:00:00",
  "end_time": "2025-11-20 15:00:00"
}
```

**Response 200**:
```json
{
  "sync_log_id": 123,
  "fetched_count": 15,
  "status": "success"
}
```

### GET /sync/logs
获取同步日志

**Query Parameters**:
- `page`: 页码(默认1)
- `page_size`: 每页数量(默认20)

**Response 200**:
```json
{
  "total": 100,
  "items": [
    {
      "id": 123,
      "sync_type": "manual",
      "status": "success",
      "start_time": "2025-11-19 14:30:00",
      "end_time": "2025-11-19 14:30:05",
      "fetched_count": 15,
      "operator": "admin"
    }
  ]
}
```

---

## Check Object Endpoints

### GET /check-objects
获取检测样品列表(支持查询过滤)

**Query Parameters**:
- `status`: 状态筛选(0/1/2)
- `company`: 公司名称(模糊查询)
- `check_no`: 质检编号(精确查询)
- `start_date`: 开始时间
- `end_date`: 结束时间
- `page`: 页码
- `page_size`: 每页数量(默认50,最大50)

**Response 200**:
```json
{
  "total": 150,
  "page": 1,
  "page_size": 50,
  "items": [
    {
      "id": 1,
      "check_object_union_num": "CN20250319001",
      "submission_goods_name": "红富士",
      "submission_person_company": "大洋智慧科技有限公司",
      "check_type": "水果",
      "status": 0,
      "check_start_time": null,
      "create_time": "2025-03-19 14:25:10"
    }
  ]
}
```

### GET /check-objects/{id}
获取样品详细信息

**Response 200**:
```json
{
  "id": 1,
  "check_object_id": 128651,
  "check_object_union_num": "CN20250319001",
  "submission_goods_name": "红富士",
  "submission_person_company": "大洋智慧科技有限公司",
  "status": 0,
  "check_items": [
    {
      "check_item_name": "吊白块(0.01)",
      "num": "47.90%抑制率",
      "result": null,
      "reference_value": "15mg/kg",
      "method_name": "比色法",
      "basic_name": "GB/T 21126-2007"
    }
  ]
}
```

### PUT /check-objects/{id}
编辑样品信息

**Request**:
```json
{
  "submission_goods_name": "红富士(修改)",
  "check_items": [
    {
      "check_item_id": 14,
      "num": "50%抑制率",
      "result": "合格"
    }
  ]
}
```

**Response 200**:
```json
{
  "id": 1,
  "message": "Updated successfully"
}
```

---

## Check Result Endpoints

### PUT /check-objects/{id}/result
录入检测结果

**Request**:
```json
{
  "check_result": "合格",
  "check_items": [
    {
      "check_item_id": 14,
      "check_item_name": "吊白块",
      "result": "合格",
      "item_indicator": "阴性"
    },
    {
      "check_item_id": 15,
      "check_item_name": "小苏打",
      "result": "合格",
      "item_indicator": "10"
    }
  ]
}
```

**Response 200**:
```json
{
  "id": 1,
  "status": 1,
  "message": "Result saved successfully"
}
```

---

## Report Endpoints

### POST /reports/upload
上传检测报告PDF

**Request**: `multipart/form-data`
- `file`: PDF文件(<10MB)
- `check_object_id`: 样品ID

**Response 200**:
```json
{
  "check_result_url": "http://localhost:8000/reports/2025/11/CN20250319001_1732012345.pdf",
  "message": "Report uploaded successfully"
}
```

### GET /reports/download/{check_no}
下载检测报告

**Response 200**: PDF文件流

### POST /reports/export-excel
导出检测结果为Excel文件

**Request**:
```json
{
  "check_object_ids": [1, 2, 3],  // 可选,指定样品ID列表
  "query": {                      // 可选,查询条件(与列表查询API相同)
    "status": 1,
    "company": "大洋智慧",
    "start_date": "2025-11-01",
    "end_date": "2025-11-30"
  }
}
```

**Response 200**: Excel文件流
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename="检测结果导出_20251119.xlsx"`

**Excel格式**:
| 列名 | 说明 | 示例 |
|-----|------|------|
| 样品名称 | submission_goods_name | 红富士 |
| 公司/个体 | submission_person_company | 振东远大 京MFG076 |
| 检测项目 | check_item_name | 氯霉素 |
| 检验结果 | num | 阴性 / 72.9% |
| 该项结果 | result | 合格 / 不合格 |
| 检测时间 | check_time | 2025/11/18 |
| 样品编号 | check_object_union_num | CN20251118001 |
| 检测方法 | method_name | 胶体金免疫层析法 |

**注意事项**:
- 一个样品包含多个检测项目时,每个项目生成一行
- 如果未指定check_object_ids且未提供query,导出当前所有已检测样品
- 最多导出1000行,超过时返回400错误提示分批导出

**Response 400** (数据量过大):
```json
{
  "detail": "Export limit exceeded",
  "message": "导出数据超过1000行限制,请使用查询条件筛选或分批导出",
  "total_rows": 1500
}
```

---

## Submit Result Endpoints

### POST /submit/{check_object_id}
提交检测结果到客户方API

**Response 200**:
```json
{
  "status": "success",
  "client_response": {
    "status": 200,
    "message": "操作成功"
  },
  "check_object_status": 2
}
```

**Response 400** (客户方API失败):
```json
{
  "status": "failed",
  "error": "质检编号不能为空",
  "client_response": {
    "status": 400,
    "message": "质检编号不能为空"
  }
}
```

---

## Error Responses

所有端点遵循统一错误格式:

**400 Bad Request**:
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "username",
      "message": "Username is required"
    }
  ]
}
```

**401 Unauthorized**:
```json
{
  "detail": "Token expired or invalid"
}
```

**404 Not Found**:
```json
{
  "detail": "Check object not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error",
  "error": "Database connection failed"
}
```

---

完整OpenAPI 3.0规范见: `openapi.yaml`
