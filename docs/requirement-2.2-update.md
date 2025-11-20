# 需求2.2变更记录

**日期**: 2025-11-20
**需求来源**: req.md 第2.2节
**变更类型**: 功能增强

## 需求描述

需求2.2原文：
> 支持我方检测人员提交检测结果，点击"检测结果修改"按钮支持5个核心字段的填写录入，检测项目、单位、检测结果, 检出限和检测方法。支持多行添加录入。支持上传检测报告（仅支持pdf格式）。

## 变更范围

### 1. 数据库变更

#### 数据库迁移脚本
- 文件: `backend/migrations/add_check_item_fields.sql`
- 执行状态: ✅ 已完成

```sql
-- 添加3个新字段到 check_object_items 表
ALTER TABLE check_object_items
ADD COLUMN check_method VARCHAR(200);  -- 检测方法

ALTER TABLE check_object_items
ADD COLUMN unit VARCHAR(50);           -- 单位

ALTER TABLE check_object_items
ADD COLUMN detection_limit VARCHAR(100); -- 检出限
```

#### check_object_items表新增字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| check_method | VARCHAR(200) | 检测方法 |
| unit | VARCHAR(50) | 单位 |
| detection_limit | VARCHAR(100) | 检出限 |

### 2. 后端变更

#### 模型更新
- **文件**: `backend/app/models/check_item.py`
- **变更**: CheckObjectItem模型添加3个新字段
  - `check_method` - 检测方法
  - `unit` - 单位
  - `detection_limit` - 检出限

#### Schema更新
- **文件**: `backend/app/schemas/check_object.py`
- **变更**:
  - `CheckObjectItemResponse`: 添加5个核心字段的响应
  - `CheckObjectItemUpdate`: 更新字段映射以支持5个核心字段

#### API更新
- **文件**: `backend/app/api/check_objects.py`
- **端点**: `PUT /api/v1/check-objects/{id}/result`
- **变更**: 更新检测结果录入逻辑，支持保存5个核心字段
  - check_item_name (检测项目)
  - check_method (检测方法)
  - unit (单位)
  - num (检测结果)
  - detection_limit (检出限)
  - result (结果判定)

### 3. 前端变更

#### 组件更新
**文件**: `frontend/src/components/CheckResultForm.vue`

**新增功能**:

1. **5个核心字段表单**
   - 检测项目名称输入框
   - 检测方法输入框
   - 单位输入框 (宽度80px)
   - 检测结果输入框
   - 检出限输入框
   - 结果判定下拉框

2. **多行添加录入**
   ```vue
   <a-button type="dashed" block @click="handleAddItem">
     <template #icon><PlusOutlined /></template>
     添加检测项目
   </a-button>
   ```
   - 支持动态添加检测项目行
   - 支持删除检测项目行
   - 每行有独立的表单字段

3. **报告上传功能**
   ```vue
   <a-upload
     v-model:file-list="fileList"
     :before-upload="beforeUpload"
     accept=".pdf"
     :max-count="1"
   >
   ```
   - 仅支持PDF格式
   - 文件大小限制10MB
   - 文件验证：类型和大小校验

#### 视图更新
**文件**: `frontend/src/views/CheckDetailView.vue`

**变更**:
- 更新`handleSubmitResult`函数以支持报告上传
- 先上传报告文件，成功后再保存检测结果
- 导入`uploadReport`服务函数

### 4. 文档变更

- **data-model.md**: 更新check_object_items表结构说明
- **requirement-2.2-update.md**: 创建本变更记录文档

## 功能特性

### 1. 检测结果录入界面

**表格列**:
| 列名 | 宽度 | 说明 |
|------|------|------|
| 检测项目 | 150px | 可编辑输入框 |
| 检测方法 | 150px | 可编辑输入框 |
| 单位 | 100px | 可编辑输入框 |
| 检测结果 | 120px | 可编辑输入框 |
| 检出限 | 120px | 可编辑输入框 |
| 结果判定 | 120px | 下拉选择(合格/不合格/基本合格) |
| 操作 | 80px | 删除按钮 |

### 2. 数据验证规则

**必填项**:
- 检验结果(整体): 必填

**可选项**:
- 检测项目名称
- 检测方法
- 单位
- 检测结果
- 检出限
- 结果判定

**提交验证**:
- 至少填写一个检测项目
- 如果上传报告，必须是PDF格式，不超过10MB

### 3. 工作流程

1. 检测人员点击"录入检测结果"按钮
2. 在弹出的模态框中：
   - 选择整体检验结果(合格/不合格/基本合格)
   - 填写检测项目明细（可添加多行）
   - 可选：上传PDF格式检测报告
3. 点击"保存结果"
4. 系统先上传报告(如果有)
5. 然后保存检测结果数据
6. 样品状态从"待检测(0)"变更为"已检测(1)"

## 兼容性说明

### 向后兼容
- 新字段均为可选(NULL)，不影响现有数据
- 现有API端点保持兼容
- 数据库迁移使用`ADD COLUMN IF NOT EXISTS`确保安全

### 数据迁移
- 现有检测项目记录的新字段将为NULL
- 不需要数据回填

## 测试建议

### 单元测试
1. 测试check_method, unit, detection_limit字段的存储和检索
2. 测试多行添加和删除功能
3. 测试PDF上传验证逻辑

### 集成测试
1. 测试完整的检测结果录入流程
2. 测试报告上传+结果保存的组合流程
3. 测试字段验证规则

### UI测试
1. 验证5个核心字段的表单布局
2. 验证添加/删除行功能
3. 验证PDF上传组件
4. 验证错误提示信息

## 部署清单

### 数据库
- [x] 执行迁移脚本: `backend/migrations/add_check_item_fields.sql`

### 后端
- [x] 更新模型: `backend/app/models/check_item.py`
- [x] 更新Schema: `backend/app/schemas/check_object.py`
- [x] 更新API: `backend/app/api/check_objects.py`

### 前端
- [x] 更新组件: `frontend/src/components/CheckResultForm.vue`
- [x] 更新视图: `frontend/src/views/CheckDetailView.vue`

### 文档
- [x] 更新数据模型文档: `specs/1-food-quality-system/data-model.md`
- [x] 创建变更记录: `docs/requirement-2.2-update.md`

## 回滚方案

如需回滚此变更：

```sql
-- 删除新增字段
ALTER TABLE check_object_items DROP COLUMN IF EXISTS check_method;
ALTER TABLE check_object_items DROP COLUMN IF EXISTS unit;
ALTER TABLE check_object_items DROP COLUMN IF EXISTS detection_limit;
```

然后还原代码到变更前的版本。

## 相关文档

- [原始需求文档](../req.md) - 第2.2节
- [数据模型文档](../specs/1-food-quality-system/data-model.md)
- [API文档](./api.md)

## 签署

- **开发人员**: Claude Code
- **审核人员**: 待审核
- **部署日期**: 2025-11-20
