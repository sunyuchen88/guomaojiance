# Data Model: 食品质检系统

**Feature**: 食品质检系统
**Date**: 2025-11-19
**Database**: PostgreSQL 15+

## Entity-Relationship Diagram

```
[User] 1──────────* [CheckObject]
                     │
                     │ 1
                     │
                     │ *
                   [CheckObjectItem]
                     │
                     │ *
                     │
                     │ 1
                   [CheckItem]

[SyncLog] (独立表,记录同步历史)
[SystemConfig] (独立表,系统配置)
```

## Tables

### 1. users (用户表)

**Purpose**: 存储检测人员账号信息

| 列名            | 类型           | 约束                      | 说明                  |
| ------------- | ------------ | ----------------------- | ------------------- |
| id            | SERIAL       | PRIMARY KEY             | 用户ID                |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL        | 登录账号                |
| password_hash | VARCHAR(255) | NOT NULL                | bcrypt哈希密码          |
| name          | VARCHAR(100) | NOT NULL                | 真实姓名                |
| role          | VARCHAR(20)  | NOT NULL                | 角色(inspector/admin) |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW() | 创建时间                |
| last_login_at | TIMESTAMP    | NULL                    | 最后登录时间              |

**Indexes**:

- `idx_users_username` ON (username) - 加速登录查询

**Validation Rules**:

- `username`: 3-50字符,仅字母数字下划线
- `password`: 最少8字符(应用层验证)
- `role`: ENUM('inspector', 'admin')

---

### 2. check_objects (检测样品表)

**Purpose**: 存储从客户方API获取的待检测样品信息

| 列名                          | 类型           | 约束                  | 说明                    |
| --------------------------- | ------------ | ------------------- | --------------------- |
| id                          | SERIAL       | PRIMARY KEY         | 内部ID                  |
| check_object_id             | BIGINT       | UNIQUE, NOT NULL    | 客户方质检对象ID             |
| day_num                     | VARCHAR(10)  | NULL                | 日期编号(如001)            |
| check_object_union_num      | VARCHAR(50)  | NOT NULL            | 质检联合编号(CN20250319001) |
| code_url                    | TEXT         | NULL                | 二维码URL                |
| submission_goods_id         | INTEGER      | NULL                | 送检货物ID                |
| submission_goods_name       | VARCHAR(200) | NULL                | 样品名称(如红富士)            |
| submission_goods_area       | VARCHAR(100) | NULL                | 产地(如青海省)              |
| submission_goods_location   | VARCHAR(200) | NULL                | 位置(如B备菜厅)             |
| submission_goods_unit       | VARCHAR(20)  | NULL                | 单位(如001)              |
| submission_goods_car_number | VARCHAR(20)  | NULL                | 车牌号                   |
| submission_method           | VARCHAR(50)  | NULL                | 送检方式(如个人送检)           |
| submission_person           | VARCHAR(100) | NULL                | 送检人                   |
| submission_person_mobile    | VARCHAR(20)  | NULL                | 送检人手机                 |
| submission_person_company   | VARCHAR(200) | NULL                | 送检公司                  |
| driver                      | VARCHAR(100) | NULL                | 司机姓名                  |
| driver_mobile               | VARCHAR(20)  | NULL                | 司机手机                  |
| check_type                  | VARCHAR(50)  | NULL                | 检测类型(如水果)             |
| status                      | SMALLINT     | NOT NULL, DEFAULT 0 | 状态(0=待检测,1=已检测,2=已提交) |
| is_receive                  | SMALLINT     | DEFAULT 1           | 是否接收                  |
| check_start_time            | TIMESTAMP    | NULL                | 检测开始时间                |
| check_end_time              | TIMESTAMP    | NULL                | 检测结束时间                |
| check_result                | VARCHAR(20)  | NULL                | 总体检测结果(合格/不合格)        |
| check_result_url            | TEXT         | NULL                | 报告PDF URL             |
| create_admin                | VARCHAR(100) | NULL                | 创建人                   |
| create_time                 | TIMESTAMP    | DEFAULT NOW()       | 创建时间(客户方)             |
| synced_at                   | TIMESTAMP    | DEFAULT NOW()       | 同步到本地时间               |
| updated_at                  | TIMESTAMP    | DEFAULT NOW()       | 本地更新时间                |

**Indexes**:

- `idx_check_objects_status` ON (status) - 状态筛选
- `idx_check_objects_union_num` ON (check_object_union_num) - 编号查询
- `idx_check_objects_company` ON (submission_person_company) - 公司查询
- `idx_check_objects_check_start_time` ON (check_start_time) - 时间范围查询
- `idx_check_objects_check_object_id` ON (check_object_id) - 客户方ID查询

**State Transitions**:

```
[待检测(0)] --录入检测结果--> [已检测(1)] --提交成功--> [已提交(2)]
                                     |
                                     --提交失败--> [已检测(1)]
```

**Validation Rules**:

- `status`: 0 | 1 | 2
- `check_object_union_num`: 必须唯一
- `check_result_url`: 必须以http开头的有效URL

---

### 3. check_object_items (检测项目明细表)

**Purpose**: 存储每个样品的具体检测项目和结果

**T2.2更新**: 添加5个核心字段 - 检测项目、检测方法、单位、检测结果、检出限

| 列名                   | 类型           | 约束                           | 说明                       |
| -------------------- | ------------ | ---------------------------- | ------------------------ |
| id                   | SERIAL       | PRIMARY KEY                  | 内部ID                     |
| check_object_item_id | BIGINT       | UNIQUE, NOT NULL             | 客户方检测项目明细ID              |
| check_object_id      | BIGINT       | NOT NULL, FK → check_objects | 关联样品ID                   |
| check_item_id        | INTEGER      | NOT NULL                     | 检测项目ID                   |
| check_item_name      | VARCHAR(200) | NOT NULL                     | **T2.2** 检测项目名称(如吊白块)    |
| check_method         | VARCHAR(200) | NULL                         | **T2.2** 检测方法(如比色法)      |
| unit                 | VARCHAR(50)  | NULL                         | **T2.2** 单位(如mg/kg)      |
| num                  | VARCHAR(50)  | NULL                         | **T2.2** 检测结果数值(如47.90%) |
| detection_limit      | VARCHAR(100) | NULL                         | **T2.2** 检出限(如0.01mg/kg) |
| result               | VARCHAR(20)  | NULL                         | 结果判定(合格/不合格或空)           |
| check_time           | TIMESTAMP    | NULL                         | 检测时间                     |
| check_admin          | VARCHAR(100) | NULL                         | 检测人员                     |
| status               | SMALLINT     | DEFAULT 1                    | 状态                       |
| create_time          | TIMESTAMP    | DEFAULT NOW()                | 创建时间                     |
| reference_value      | VARCHAR(100) | NULL                         | 参考值(如15mg/kg)            |
| item_indicator       | VARCHAR(200) | NULL                         | 指标描述                     |

**Indexes**:

- `idx_check_object_items_check_object_id` ON (check_object_id) - 关联查询

**Foreign Keys**:

- `fk_check_object_items_check_object` FOREIGN KEY (check_object_id) REFERENCES check_objects(check_object_id) ON DELETE CASCADE

**Validation Rules**:

- `result`: NULL | '合格' | '不合格' | '基本合格'
- 级联删除: 删除样品时自动删除所有关联检测项目

**T2.2 Requirements**:

支持检测人员录入5个核心字段：
1. 检测项目 (check_item_name)
2. 检测方法 (check_method)
3. 单位 (unit)
4. 检测结果 (num)
5. 检出限 (detection_limit)

支持多行添加录入，支持上传PDF格式检测报告

---

### 4. check_items (检测项目基础表)

**Purpose**: 存储检测项目的基础信息(检测方法、依据、指标)

| 列名               | 类型             | 约束               | 说明                     |
| ---------------- | -------------- | ---------------- | ---------------------- |
| id               | SERIAL         | PRIMARY KEY      | 内部ID                   |
| item_id          | INTEGER        | UNIQUE, NOT NULL | 客户方检测项ID               |
| name             | VARCHAR(200)   | NOT NULL         | 检测项目名称(如吊白块(0.01))     |
| method_id        | INTEGER        | NULL             | 检测方法ID                 |
| method_name      | VARCHAR(200)   | NULL             | 检测方法名称(如比色法)           |
| basic_id         | INTEGER        | NULL             | 检测依据ID                 |
| basic_name       | VARCHAR(500)   | NULL             | 检测依据(如GB/T 21126-2007) |
| indicators_id    | INTEGER        | NULL             | 检测指标ID                 |
| indicators_name  | VARCHAR(200)   | NULL             | 检测指标名称(如超标/未超标)        |
| reference_values | VARCHAR(100)   | NULL             | 参考值(如15mg/kg)          |
| fee              | DECIMAL(10, 2) | DEFAULT 0.01     | 费用                     |
| created_at       | TIMESTAMP      | DEFAULT NOW()    | 创建时间                   |

**Indexes**:

- `idx_check_items_item_id` ON (item_id) - 客户方ID查询
- `idx_check_items_name` ON (name) - 名称查询

**Validation Rules**:

- `fee`: >= 0

---

### 5. sync_logs (数据同步日志表)

**Purpose**: 记录每次数据同步操作的详细信息

| 列名            | 类型           | 约束                      | 说明                             |
| ------------- | ------------ | ----------------------- | ------------------------------ |
| id            | SERIAL       | PRIMARY KEY             | 日志ID                           |
| sync_type     | VARCHAR(20)  | NOT NULL                | 同步类型(auto/manual)              |
| status        | VARCHAR(20)  | NOT NULL                | 状态(success/failed/in_progress) |
| start_time    | TIMESTAMP    | NOT NULL, DEFAULT NOW() | 开始时间                           |
| end_time      | TIMESTAMP    | NULL                    | 结束时间                           |
| fetched_count | INTEGER      | DEFAULT 0               | 拉取数量                           |
| error_message | TEXT         | NULL                    | 错误信息(失败时)                      |
| operator      | VARCHAR(100) | NULL                    | 操作人(手动触发时)                     |

**Indexes**:

- `idx_sync_logs_start_time` ON (start_time DESC) - 按时间查询

**Validation Rules**:

- `sync_type`: 'auto' | 'manual'
- `status`: 'success' | 'failed' | 'in_progress'

---

### 6. system_config (系统配置表)

**Purpose**: 存储系统配置信息(单行表)

| 列名                    | 类型           | 约束                         | 说明               |
| --------------------- | ------------ | -------------------------- | ---------------- |
| id                    | SERIAL       | PRIMARY KEY                | 配置ID(固定为1)       |
| api_base_url          | VARCHAR(500) | NOT NULL                   | 客户方API基础URL      |
| client_app_id         | VARCHAR(100) | NOT NULL                   | 客户方app_id        |
| client_secret         | VARCHAR(255) | NOT NULL                   | 客户方密钥(加密存储)      |
| sync_interval_minutes | INTEGER      | DEFAULT 30                 | 自动同步间隔(分钟)       |
| file_storage_path     | VARCHAR(500) | DEFAULT '/uploads/reports' | 文件存储路径           |
| server_domain         | VARCHAR(200) | NOT NULL                   | 服务器域名(用于生成报告URL) |
| updated_at            | TIMESTAMP    | DEFAULT NOW()              | 更新时间             |

**Constraints**:

- 确保仅有一行配置: `CHECK (id = 1)`

**Validation Rules**:

- `sync_interval_minutes`: >= 1
- `api_base_url`: 必须以http开头

---

## Database Initialization

### Alembic Migration Script

```python
"""Initial schema

Revision ID: 001
Create Date: 2025-11-19
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('idx_users_username', 'users', ['username'])

    # Create check_objects table
    op.create_table(
        'check_objects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('check_object_id', sa.BigInteger, unique=True, nullable=False),
        sa.Column('check_object_union_num', sa.String(50), nullable=False),
        sa.Column('submission_person_company', sa.String(200)),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='0'),
        sa.Column('check_start_time', sa.TIMESTAMP),
        sa.Column('check_result_url', sa.Text),
        # ... 其他字段
        sa.Column('synced_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )
    op.create_index('idx_check_objects_status', 'check_objects', ['status'])
    op.create_index('idx_check_objects_union_num', 'check_objects', ['check_object_union_num'])
    # ... 其他索引

    # Create other tables...
    # check_object_items, check_items, sync_logs, system_config

    # Insert default system config
    op.execute("""
        INSERT INTO system_config (id, api_base_url, client_app_id, client_secret, server_domain)
        VALUES (1, 'https://test1.yunxianpei.com', '689_abc', 'encrypted_67868790', 'http://localhost:8000')
    """)

    # Insert default admin user (password: admin123)
    op.execute("""
        INSERT INTO users (username, password_hash, name, role)
        VALUES ('admin', '$2b$12$...bcrypt_hash...', '管理员', 'admin')
    """)

def downgrade():
    op.drop_table('system_config')
    op.drop_table('sync_logs')
    op.drop_table('check_object_items')
    op.drop_table('check_items')
    op.drop_table('check_objects')
    op.drop_table('users')
```

---

## Data Volume Estimates

**第一年预估**:

- Users: ~10条
- CheckObjects: ~3,000条 (100-500/月 × 12月)
- CheckObjectItems: ~15,000条 (每个样品平均5个检测项目)
- CheckItems: ~200条 (检测项目基础数据相对固定)
- SyncLogs: ~17,500条 (每30分钟一次 × 24小时 × 365天)
- SystemConfig: 1条

**存储空间估算**:

- 数据库: <500MB (第一年)
- PDF文件: 6-30GB (年度300-3000份 × 2-10MB/份)
- **总计**: <31GB,满足本地存储方案

---

## Performance Optimization

**索引策略**:

- 为所有外键创建索引(check_object_id等)
- 为查询条件字段创建索引(status, check_object_union_num, submission_person_company, check_start_time)
- 避免为低基数字段创建索引(is_receive, role)

**查询优化**:

- 使用LIMIT/OFFSET分页,避免全表扫描
- 时间范围查询使用B-tree索引
- 复杂查询考虑使用EXPLAIN ANALYZE分析执行计划

**数据清理**:

- SyncLogs定期归档(保留最近90天)
- 已提交样品超过2年后可归档到历史表
