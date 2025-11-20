# 需求文档变更对比分析

**日期**: 2025-11-20
**文档**: req.md 重大更新

## 📋 主要变化点

### 1. 列表页布局变化（需求2.1-2.4）

#### 原需求
- 检测信息列表
- 基本的查询筛选功能
- 简单的导出功能

#### 新需求
**右上方按钮顺序**：
```
[获取数据] [导出Excel] [报告下载]
```

**具体变化**：
1. **获取数据按钮** (2.1)
   - 位置：列表页右上方
   - 功能：从客户方接口获取数据，刷新同步
   - 点击"编辑"进入详情页

2. **导出Excel按钮** (2.2)
   - 位置：在"获取数据"按钮右边
   - 功能：支持多维度筛选（参考2.3）后导出
   - 导出字段见原需求文档图片

3. **报告下载按钮** (2.4) - **新增功能**
   - 位置：在"导出Excel"按钮右边
   - 功能：支持多维度筛选后批量下载PDF报告
   - 下载的是用户上传的检测报告PDF文件

### 2. 筛选功能增强（需求2.3）

#### 原筛选维度
- 状态
- 公司名称
- 检测编号

#### 新筛选维度
- 状态
- 公司名称
- 检测编号
- **采样起始时间段** ⭐ 新增
- **检测结果** ⭐ 新增

### 3. 详情页重大调整（需求2.5）

#### 2.5.1 样品基本信息字段

| 字段 | 来源 | 是否可编辑 | 备注 |
|------|------|-----------|------|
| 状态 | 自动 | ❌ | 待检测/已检测/已提交 |
| 样品名称 | submission_goods_name | ✅ | |
| 样品编号 | check_object_union_num | ✅ | |
| 委托单位名称 | submission_person_company | ✅ | |
| 委托单位地址 | 手工填写 | ✅ | 留空 |
| 生产日期 | 默认"/" | ✅ | |
| 样品数量 | 手工填写 | ✅ | |
| 样品类别 | check_type | ✅ | |
| 样品状态 | status | ✅ | |
| 联系人 | submission_person | ✅ | |
| 联系电话 | submission_person_mobile | ✅ | |
| 收样日期 | create_time | ✅ | |
| 检测日期 | 报告提交当天 | ✅ | |
| 车牌号 | submission_goods_car_number | ✅ | |
| 备注 | 手工填写 | ✅ | |

#### 2.5.2 检测项目表单字段

| 表头 | 数据来源 |
|------|----------|
| 序号 | data:list:objectItems:checkItem:item_id |
| 检验项目 | data:list:objectItems:checkItem:name |
| 单位 | data:list:objectItems:checkItem:reference_values |
| 检测结果 | 默认为空，手工填写 |
| 检出限 | data:list:objectItems:checkItem:fee |
| 检测方法 | data:list:objectItems:checkItem:method_name |

**注意**：这与之前实现的字段映射不同！

#### 2.5.3 表单下方操作

1. **总体检测结果**：选项（合格/不合格）
2. **上传检测报告**：支持上传PDF，后台生成URL

#### 2.5.4 页面按钮

- **返回列表**：返回列表页
- **保存修改**：保存所有修改包括报告上传

### 4. 列表页操作按钮（需求2.6）

每条记录的操作列：
- **编辑**按钮：进入详情页编辑
- **提交检测**按钮：调用3.2接口上传数据到客户方

## 🔄 需要调整的内容

### 后端调整

#### 1. 数据模型需要新增字段
```python
CheckObject:
  - 委托单位地址 (commission_unit_address)
  - 生产日期 (production_date)
  - 样品数量 (sample_quantity)
  - 检测日期 (inspection_date)
```

#### 2. API调整
- 调整字段映射关系
- 支持时间范围筛选
- 支持检测结果筛选
- 批量下载报告接口

### 前端调整

#### 1. 主列表页 (HomeView.vue / CheckListView.vue)

**布局调整**：
```vue
<template>
  <div class="list-header">
    <!-- 右上方按钮组 -->
    <a-space>
      <a-button type="primary" @click="handleFetchData">
        获取数据
      </a-button>
      <a-button @click="showExportModal">
        导出Excel
      </a-button>
      <a-button @click="showDownloadReportsModal">
        报告下载
      </a-button>
    </a-space>
  </div>

  <!-- 筛选区域 -->
  <a-form layout="inline">
    <a-form-item label="状态">...</a-form-item>
    <a-form-item label="公司名称">...</a-form-item>
    <a-form-item label="检测编号">...</a-form-item>
    <a-form-item label="采样起始时间">
      <a-range-picker />  <!-- 新增 -->
    </a-form-item>
    <a-form-item label="检测结果">
      <a-select>  <!-- 新增 -->
        <a-select-option value="合格">合格</a-select-option>
        <a-select-option value="不合格">不合格</a-select-option>
      </a-select>
    </a-form-item>
  </a-form>

  <!-- 表格操作列 -->
  <a-table>
    <template #action="{ record }">
      <a-button @click="handleEdit(record)">编辑</a-button>
      <a-button @click="handleSubmit(record)">提交检测</a-button>
    </template>
  </a-table>
</template>
```

#### 2. 详情页 (CheckDetailView.vue)

**字段映射调整**：
```javascript
// 样品基本信息
const basicFields = {
  status: '状态',           // 不可编辑
  sample_name: '样品名称',
  sample_no: '样品编号',
  commission_unit: '委托单位名称',
  commission_address: '委托单位地址',  // 新增
  production_date: '生产日期',          // 新增，默认"/"
  sample_quantity: '样品数量',          // 新增
  sample_category: '样品类别',
  sample_status: '样品状态',
  contact_person: '联系人',
  contact_phone: '联系电话',
  receive_date: '收样日期',
  inspection_date: '检测日期',          // 新增
  vehicle_no: '车牌号',
  remark: '备注'
}

// 检测项目表单
const checkItemFields = {
  serial_no: 'item_id',           // 序号
  test_item: 'name',              // 检验项目
  unit: 'reference_values',       // 单位
  test_result: '',                // 检测结果（手工填写）
  detection_limit: 'fee',         // 检出限
  test_method: 'method_name'      // 检测方法
}
```

#### 3. 新增功能组件

**ReportBatchDownload.vue**：
- 批量下载PDF报告
- 支持筛选条件
- 打包下载或单独下载

## 📝 实施计划

### Phase 1: 数据模型和后端调整
1. 添加新字段到CheckObject模型
2. 创建数据库迁移脚本
3. 更新Schema和API
4. 添加批量下载报告接口

### Phase 2: 前端列表页调整
1. 调整按钮布局和顺序
2. 添加时间范围筛选
3. 添加检测结果筛选
4. 调整表格操作列

### Phase 3: 前端详情页调整
1. 更新字段映射关系
2. 调整样品基本信息表单
3. 调整检测项目表单
4. 更新按钮布局

### Phase 4: 新增批量下载功能
1. 创建ReportBatchDownload组件
2. 实现批量下载逻辑
3. 集成到列表页

### Phase 5: 测试和文档更新
1. 完整功能测试
2. 更新API文档
3. 更新数据模型文档
4. 更新用户操作手册

## ⚠️ 重要提醒

1. **字段映射变化**：
   - 单位：从 `unit` 改为 `reference_values`
   - 检出限：从 `detection_limit` 改为 `fee`

2. **新增必填字段**：
   - 委托单位地址
   - 生产日期
   - 样品数量
   - 检测日期

3. **向后兼容性**：
   - 现有数据可能缺少新字段
   - 需要提供默认值或迁移脚本

4. **报告批量下载**：
   - 需要处理大文件打包
   - 考虑超时和性能问题
