# 需求合规性检查报告 - 第二轮

**日期**: 2025-11-20
**检查范围**: 详情页实现 vs req.md 需求2.5
**检查结果**: 发现4个严重不符项

---

## 🔴 严重不符项

### P0-4: 详情页检测项目表格列定义不符合需求2.5.2

**需求要求** (需求2.5.2):
```
| 表头  | 序号 | 检验项目 | 单位 | 检测结果 | 检出限 | 检测方法 |
| 取值  | checkItem:item_id | checkItem:name | checkItem:reference_values | 默认为空 | checkItem:fee | checkItem:method_name |
```

**当前实现** (`frontend/src/views/CheckDetailView.vue` 第231-257行):
```javascript
const itemColumns = [
  { title: '检测项目', dataIndex: 'check_item_name' },      // ✓
  { title: '检测方法', dataIndex: 'check_method' },          // ✓
  { title: '标准值', dataIndex: 'standard_value' },         // ❌ 应该是"单位"
  { title: '检测结果', dataIndex: 'check_result' },         // ✓
  { title: '结果判定', dataIndex: 'result_indicator' },     // ❌ 应该是"检出限"
];
```

**问题**:
1. ❌ **缺少"序号"列** - 应显示 `item_id` 或 `check_item_id`
2. ❌ **"标准值"列错误** - 应改为"单位"，dataIndex改为 `unit`
3. ❌ **"结果判定"列错误** - 应改为"检出限"，dataIndex改为 `detection_limit`
4. ❌ **列顺序错误** - 应按需求顺序：序号、检验项目、单位、检测结果、检出限、检测方法

**影响**: 详情页显示的检测项目信息与需求字段不匹配

**修复方案**:
```javascript
const itemColumns = [
  { title: '序号', dataIndex: 'check_item_id', key: 'check_item_id', width: 80 },
  { title: '检验项目', dataIndex: 'check_item_name', key: 'check_item_name', width: 150 },
  { title: '单位', dataIndex: 'unit', key: 'unit', width: 100 },
  { title: '检测结果', dataIndex: 'check_result', key: 'check_result', width: 120 },
  { title: '检出限', dataIndex: 'detection_limit', key: 'detection_limit', width: 100 },
  { title: '检测方法', dataIndex: 'check_method', key: 'check_method', width: 150 },
];
```

---

### P0-5: 详情页缺少"总体检测结果"和"上传检测报告"直接显示（需求2.5.3）

**需求要求** (需求2.5.3):
> "检测项目表单下方，有2项：
> 1. '总体检测结果'，是个选项，合格/不合格可供人工选择
> 2. 上传检测报告，支持上传pdf报告"

**当前实现**:
- ❌ 详情页主界面没有"总体检测结果"选择框
- ❌ 详情页主界面没有"上传检测报告"功能
- ❌ 这两项功能被放在"录入检测结果"模态框中（`CheckResultForm`组件）

**需求设计的布局**:
```
详情页:
  ├─ 样品基本信息卡片
  ├─ 检测项目表单卡片
  └─ 检测结果卡片 ← 应该在这里！
       ├─ 总体检测结果: [合格/不合格]
       └─ 上传检测报告: [选择文件]
```

**当前实现的布局**:
```
详情页:
  ├─ 样品基本信息卡片
  ├─ 检测项目表单卡片（只读）
  └─ [录入检测结果按钮] → 打开模态框
       └─ CheckResultForm模态框
            ├─ 总体检测结果
            └─ 上传检测报告
```

**影响**:
- 用户体验不符合需求设计（需要打开模态框才能操作）
- 不符合需求2.5.3的直接显示要求
- 不符合需求2.5.4"保存修改"按钮保存所有修改的要求

**修复方案**:
在 `CheckDetailView.vue` 的检测项目表格下方添加一个新的卡片：
```vue
<a-card v-if="checkObject" title="检测结果" style="margin-top: 16px">
  <a-form layout="vertical">
    <a-form-item label="总体检测结果">
      <a-select v-model:value="editForm.check_result" placeholder="请选择">
        <a-select-option value="合格">合格</a-select-option>
        <a-select-option value="不合格">不合格</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item label="上传检测报告">
      <a-upload :before-upload="beforeUpload" accept=".pdf">
        <a-button><UploadOutlined /> 选择PDF文件</a-button>
      </a-upload>
    </a-form-item>
  </a-form>
</a-card>
```

---

### P0-6: 详情页检测项目表格不可编辑（需求2.5.2）

**需求要求** (需求2.5.2):
> "详情页下方是检测项目的表单，数据从3.1接口部分获取到待检测数据，**所有字段支持人工编辑**"

**当前实现**:
- ❌ 详情页的检测项目表格是**只读**的（第122-141行）
- ❌ 需要点击"录入检测结果"按钮打开模态框才能编辑
- ❌ 编辑后的数据通过 `saveCheckResult` API保存，不是通过"保存修改"按钮

**需求设计的交互流程**:
```
1. 打开详情页
2. 直接在详情页编辑样品信息、检测项目、总体结果、上传报告
3. 点击"保存修改"按钮 → 保存所有修改
```

**当前实现的交互流程**:
```
1. 打开详情页
2. 编辑样品信息 → 点击"保存修改" → 只保存样品信息
3. 点击"录入检测结果"按钮 → 打开模态框
4. 在模态框编辑检测项目 → 点击"保存结果" → 单独保存检测结果
```

**影响**:
- 交互流程与需求不符
- 用户需要两次保存操作，而需求设计是一次保存所有修改
- 不符合需求2.5.4的"保存修改"按钮功能

**修复方案**:
将检测项目表格改为可编辑表格（类似CheckResultForm的实现），并将数据绑定到editForm，在handleSave中一起保存。

---

### P0-7: 详情页按钮布局可能不符（需求2.5.4）

**需求要求** (需求2.5.4):
> "详情页右上方有'返回列表'和'保存修改'两个按钮"

**当前实现** (`CheckDetailView.vue` 第7-28行):
```vue
<template #extra>
  <a-space>
    <a-button @click="handleBack">返回列表</a-button>         ✓
    <a-button v-if="status === 0" @click="showResultModal">
      录入检测结果                                             ❌ 多余
    </a-button>
    <a-button v-if="status === 1" @click="showSubmitModal">
      提交检测结果                                             ❌ 多余
    </a-button>
    <a-button type="primary" @click="handleSave">
      保存修改                                                 ✓
    </a-button>
  </a-space>
</template>
```

**问题**:
- 需求只要求2个按钮，但当前实现有4个按钮
- "录入检测结果"按钮是因为当前架构需要模态框编辑
- "提交检测结果"按钮的位置可能不对（需求2.6说应该在列表页）

**需求2.6的描述**:
> "在列表页'编辑'按钮右边有'提交检测'按钮"

这说明"提交检测"按钮应该**只在列表页**，不应该在详情页。

**当前实现**:
- ✓ 列表页有"提交检测"按钮（P0-3已修复）
- ❌ 详情页也有"提交检测结果"按钮（多余）

**修复方案**:
如果P0-5和P0-6修复后（详情页直接编辑），详情页按钮应该简化为：
```vue
<template #extra>
  <a-space>
    <a-button @click="handleBack">返回列表</a-button>
    <a-button type="primary" @click="handleSave">保存修改</a-button>
  </a-space>
</template>
```

---

## 📊 问题优先级评估

| 不符项 | 优先级 | 影响范围 | 修复难度 | 说明 |
|-------|--------|----------|----------|------|
| P0-4 | **高** | 详情页显示 | 简单 | 修改列定义即可 |
| P0-5 | **高** | 页面布局 | 中等 | 需要重新布局详情页 |
| P0-6 | **高** | 交互流程 | 困难 | 需要改为可编辑表格，重构保存逻辑 |
| P0-7 | **中** | 按钮布局 | 简单 | 移除多余按钮 |

---

## 🔄 架构问题分析

### 根本原因
当前实现采用了"模态框编辑"的设计模式，而需求要求的是"页面内直接编辑"。

### 当前架构
```
详情页（只读展示） + 模态框（编辑）
```

### 需求架构
```
详情页（直接编辑所有内容）
```

### 修复策略

**方案A: 完全重构详情页（推荐）**
- 移除CheckResultForm模态框
- 在详情页直接实现可编辑检测项目表格
- 添加"总体检测结果"和"上传报告"到详情页
- 统一保存逻辑（一次保存所有修改）
- 修复成本：高，但完全符合需求

**方案B: 最小修复（权宜之计）**
- 仅修复P0-4（表格列定义）
- 保持当前模态框编辑模式
- 在详情页添加"总体检测结果"和"上传报告"的只读显示
- 修复成本：低，但交互流程仍不完全符合需求

---

## 建议

1. **紧急**: 先修复P0-4（表格列定义），这是数据显示错误
2. **重要**: 确认需求意图 - 用户是否接受当前的模态框编辑模式？
3. **长期**: 如果严格遵循需求，需要执行方案A完全重构详情页

---

## 已修复的不符项（Phase 6）

✅ P0-1: 检测项目字段映射（unit, detection_limit）
✅ P0-2: 详情页补全5个缺失字段
✅ P0-3: 列表页操作列按钮

## 新发现的不符项（本次检查）

❌ P0-4: 详情页检测项目表格列定义
❌ P0-5: 详情页缺少总体结果和上传报告直接显示
❌ P0-6: 详情页检测项目表格不可编辑
❌ P0-7: 详情页按钮布局有多余按钮
