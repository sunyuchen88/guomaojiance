# 需求文档调整实施指南

**日期**: 2025-11-20
**需求文档**: req.md (更新版本)
**影响范围**: 前端和后端大部分功能

## 🎯 总体评估

根据新需求文档分析，本次调整是**重大变更**，涉及：
- 📁 **15+ 个文件需要修改**
- ⏱️ **预计工作量**: 6-8小时
- 🔄 **数据库迁移**: 需要
- 📝 **文档更新**: 需要

**建议**: 分阶段实施，每个阶段测试后再继续

## 📋 已完成工作

### 1. 需求分析
✅ 创建需求变更对比文档: `docs/requirement-change-analysis.md`

### 2. 数据库层
✅ 更新CheckObject模型添加4个新字段:
   - `commission_unit_address` - 委托单位地址
   - `production_date` - 生产日期
   - `sample_quantity` - 样品数量
   - `inspection_date` - 检测日期

✅ 创建数据库迁移脚本: `backend/migrations/add_sample_basic_info_fields.sql`

## 🔄 待实施工作清单

### Phase 1: 后端API调整 (2-3小时)

#### 1.1 更新Schema (`backend/app/schemas/check_object.py`)
```python
# 需要添加的字段
class CheckObjectDetailResponse(BaseModel):
    # ... 现有字段 ...
    commission_unit_address: Optional[str] = None
    production_date: Optional[str] = "/"
    sample_quantity: Optional[str] = None
    inspection_date: Optional[str] = None
```

#### 1.2 更新API端点 (`backend/app/api/check_objects.py`)

**新增筛选条件**:
```python
@router.get("")
def get_check_objects(
    # ... 现有参数 ...
    check_result: Optional[str] = None,  # 新增：检测结果筛选
    start_date: Optional[date] = None,   # 新增：采样起始时间
    end_date: Optional[date] = None,     # 新增：采样结束时间
):
    # 添加筛选逻辑
    if check_result:
        query = query.filter(CheckObject.check_result == check_result)
    if start_date:
        query = query.filter(CheckObject.check_start_time >= start_date)
    if end_date:
        query = query.filter(CheckObject.check_start_time <= end_date)
```

#### 1.3 新增批量下载报告API (`backend/app/api/reports.py`)

```python
@router.post("/batch-download")
async def batch_download_reports(
    request: ReportBatchDownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量下载检测报告PDF
    需求2.4: 支持多维度筛选后批量下载
    """
    # 1. 根据筛选条件获取check_objects
    # 2. 收集所有check_result_url
    # 3. 打包成ZIP或返回文件列表
    pass
```

### Phase 2: 前端主列表页调整 (2-3小时)

#### 2.1 调整HomeView.vue布局

**当前布局**:
```
[搜索区域]
[数据表格]
[操作按钮] - 在每行
```

**新布局**:
```
[右上方操作栏]
  - 获取数据 按钮
  - 导出Excel 按钮
  - 报告下载 按钮

[搜索筛选区域]
  - 状态
  - 公司名称
  - 检测编号
  - 采样起始时间段 (DateRangePicker)
  - 检测结果 (Select)

[数据表格]
  操作列：[编辑] [提交检测]
```

#### 2.2 添加新筛选字段

```vue
<a-form-item label="采样时间段">
  <a-range-picker
    v-model:value="searchForm.dateRange"
    format="YYYY-MM-DD"
    @change="handleSearch"
  />
</a-form-item>

<a-form-item label="检测结果">
  <a-select
    v-model:value="searchForm.check_result"
    placeholder="请选择检测结果"
    allowClear
  >
    <a-select-option value="合格">合格</a-select-option>
    <a-select-option value="不合格">不合格</a-select-option>
  </a-select>
</a-form-item>
```

#### 2.3 创建ReportBatchDownload组件

`frontend/src/components/ReportBatchDownload.vue`:
```vue
<template>
  <a-modal
    v-model:open="visible"
    title="批量下载报告"
    @ok="handleDownload"
  >
    <a-form>
      <a-form-item label="筛选条件">
        <!-- 复用主列表的筛选条件 -->
      </a-form-item>
      <a-alert
        message="将根据筛选条件下载所有匹配的检测报告PDF"
        type="info"
      />
    </a-form>
  </a-modal>
</template>
```

### Phase 3: 前端详情页重构 (2-3小时)

#### 3.1 更新CheckDetailView.vue

**新的字段映射**:
```typescript
// 样品基本信息（需求2.5.1）
interface SampleBasicInfo {
  status: string;                    // 不可编辑
  sample_name: string;                // submission_goods_name
  sample_no: string;                  // check_object_union_num
  commission_unit: string;            // submission_person_company
  commission_address: string;         // 新增，手工填写
  production_date: string;            // 新增，默认"/"
  sample_quantity: string;            // 新增，手工填写
  sample_category: string;            // check_type
  sample_status: string;              // status
  contact_person: string;             // submission_person
  contact_phone: string;              // submission_person_mobile
  receive_date: string;               // create_time
  inspection_date: string;            // 新增，报告提交当天
  vehicle_no: string;                 // submission_goods_car_number
  remark: string;                     // 手工填写
}
```

#### 3.2 调整检测项目表单

**字段映射（需求2.5.2）**:
```typescript
interface CheckItemFormData {
  serial_no: number;        // checkItem.item_id
  test_item: string;        // checkItem.name
  unit: string;             // checkItem.reference_values ⚠️ 注意变化
  test_result: string;      // 默认空，手工填写
  detection_limit: string;  // checkItem.fee ⚠️ 注意变化
  test_method: string;      // checkItem.method_name
}
```

#### 3.3 更新页面按钮

```vue
<template>
  <a-page-header>
    <template #extra>
      <a-button @click="handleBack">返回列表</a-button>
      <a-button type="primary" @click="handleSave">保存修改</a-button>
    </template>
  </a-page-header>

  <!-- 样品基本信息 -->
  <a-card title="样品基本信息">
    <!-- 14个字段 -->
  </a-card>

  <!-- 检测项目表单 -->
  <a-card title="检测项目">
    <a-table :columns="checkItemColumns" />
  </a-card>

  <!-- 总体检测结果 + 上传报告 -->
  <a-card title="检测结果">
    <a-form-item label="总体检测结果">
      <a-select v-model:value="overallResult">
        <a-select-option value="合格">合格</a-select-option>
        <a-select-option value="不合格">不合格</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item label="上传检测报告">
      <a-upload
        :before-upload="beforeUpload"
        accept=".pdf"
      >
        <a-button>选择PDF文件</a-button>
      </a-upload>
    </a-form-item>
  </a-card>
</template>
```

### Phase 4: 数据迁移和测试 (1-2小时)

#### 4.1 执行数据库迁移
```bash
docker-compose -p food-quality exec -T postgres psql -U postgres -d food_quality < backend/migrations/add_sample_basic_info_fields.sql
```

#### 4.2 验证数据库字段
```sql
\d check_objects
-- 确认新字段已添加
```

#### 4.3 测试清单
- [ ] 数据同步正常
- [ ] 列表页筛选功能正常
- [ ] 详情页字段显示和编辑正常
- [ ] 报告上传功能正常
- [ ] 批量下载报告功能正常
- [ ] 提交检测结果正常

### Phase 5: 文档更新 (1小时)

#### 需要更新的文档
1. `specs/1-food-quality-system/spec.md` - 功能规格
2. `specs/1-food-quality-system/data-model.md` - 数据模型
3. `docs/api.md` - API文档
4. `README.md` - 用户手册

## ⚠️ 重要注意事项

### 1. 字段映射变化
**需求2.5.2中的字段映射与之前实现不同**:

| 表头 | 原实现 | 新需求 | 变化 |
|------|--------|--------|------|
| 单位 | `unit` | `reference_values` | ⚠️ 字段改变 |
| 检出限 | `detection_limit` | `fee` | ⚠️ 字段改变 |

这可能导致现有数据显示不正确！

### 2. 数据兼容性

现有数据库中的检测项目可能：
- 没有`reference_values`字段的数据（单位为空）
- 没有`fee`字段的数据（检出限为空）

**建议**：先在测试环境验证数据迁移后再应用到生产环境

### 3. 前端重构范围

由于布局和字段映射变化较大，建议：
- 详情页完全重写，而不是逐步修改
- 保留原代码做备份
- 分支开发，测试通过后合并

## 🚀 推荐实施方案

### 方案A：完整实施（推荐用于开发/测试环境）

1. 执行数据库迁移
2. 更新所有后端代码
3. 重构所有前端页面
4. 完整测试
5. 一次性部署

**优点**: 一次性完成所有调整
**缺点**: 风险较大，调试时间长

### 方案B：分阶段实施（推荐用于生产环境）

**第一阶段**: 后端调整（不影响现有功能）
- 数据库迁移
- 后端API添加新字段和筛选条件
- 保持向后兼容

**第二阶段**: 前端列表页调整
- 调整布局
- 添加新筛选条件
- 添加批量下载功能

**第三阶段**: 前端详情页重构
- 更新字段映射
- 调整页面布局

**第四阶段**: 完整测试和部署

**优点**: 风险可控，可随时回滚
**缺点**: 需要更多时间

## 📝 下一步行动

请您决定：

1. **选择实施方案**: 方案A（完整实施）还是方案B（分阶段实施）

2. **开始实施**:
   - 如选择方案A，我将立即开始修改所有文件
   - 如选择方案B，我们先完成第一阶段（后端调整）

3. **暂停并评估**:
   - 先执行数据库迁移，查看现有数据情况
   - 评估数据兼容性后再决定

请告诉我您希望如何继续？
