# 数据库说明

## 目标
本项目当前使用 SQLite 作为本地持久化数据库，使用 Python 内置 `sqlite3` 模块执行原生 SQL。

这样设计的目的有两个：
- 保持 MVP 简单，避免过早引入 ORM。
- 方便直接学习和观察 SQL 语句与表结构之间的关系。

## 数据库文件位置
- 默认运行库文件：`data/simulator.db`
- 测试库文件：`backend/tests/test.db`

默认路径由 `backend/app/core/database.py` 中的 `get_database_path()` 决定。

如果设置了环境变量 `APP_DB_PATH`，程序会优先使用这个路径。

## 当前表结构

### 1. `machines`
用于保存物理机配置。

```sql
CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_cpu INTEGER NOT NULL,
    total_memory INTEGER NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);
```

字段说明：
- `id`：主键，自增 ID。
- `name`：物理机名称。
- `total_cpu`：物理机总 CPU 容量。
- `total_memory`：物理机总内存容量。
- `enabled`：是否启用。SQLite 没有独立布尔类型，这里使用整数保存：`1` 表示 `true`，`0` 表示 `false`。

### 2. `tasks`
用于保存任务配置。

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    required_cpu INTEGER NOT NULL,
    required_memory INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    submit_time INTEGER NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    deadline INTEGER NULL
);
```

字段说明：
- `id`：主键，自增 ID。
- `name`：任务名称。
- `required_cpu`：任务需要的 CPU。
- `required_memory`：任务需要的内存。
- `duration`：任务持续时间。
- `submit_time`：任务提交时间。
- `priority`：任务优先级，默认值为 `0`。
- `deadline`：任务截止时间，可以为空。

### 3. `simulations`
用于保存一次仿真的结果。

```sql
CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm TEXT NOT NULL,
    max_time INTEGER NOT NULL,
    timeline_json TEXT NOT NULL,
    resource_history_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL
);
```

字段说明：
- `id`：主键，自增 ID。
- `algorithm`：本次仿真使用的调度算法。
- `max_time`：本次仿真的最大运行时间。
- `timeline_json`：任务执行时间线，使用 JSON 字符串保存。
- `resource_history_json`：资源利用率历史数据，使用 JSON 字符串保存。
- `metrics_json`：最终指标，使用 JSON 字符串保存。

## 为什么仿真结果先存 JSON
`timeline`、`resource_history`、`metrics` 都是结构相对复杂的数据。

MVP 阶段先把它们序列化成 JSON 字符串写入 SQLite，有几个好处：
- 实现简单，能快速跑通持久化。
- 不需要一开始就拆很多张表。
- 方便后续在前端直接读取和还原。

对应代价是：
- 不适合做复杂 SQL 查询。
- 不适合做细粒度统计分析。

如果后面要深入学习关系型设计，可以把它进一步拆成例如：
- `simulation_tasks`
- `simulation_resource_points`
- `simulation_metrics`

## 项目里实际用到的 SQL

### 1. 建表：`CREATE TABLE`
位置：`backend/app/core/database.py`

程序启动时会调用 `initialize_database()`，执行建表 SQL：
- 如果表不存在，就创建。
- 如果表已存在，就跳过。

这是通过 `CREATE TABLE IF NOT EXISTS` 完成的。

### 2. 插入数据：`INSERT INTO`
位置：`backend/app/core/store.py`

例如创建物理机时：

```sql
INSERT INTO machines (name, total_cpu, total_memory, enabled)
VALUES (?, ?, ?, ?)
```

这里的 `?` 是参数占位符，实际值由 Python 传入。

这样写的好处：
- 避免自己拼接字符串。
- 更安全，能避免常见 SQL 注入问题。
- 写法也是 `sqlite3` 的标准风格。

创建任务时也是同样方式：

```sql
INSERT INTO tasks (
    name,
    required_cpu,
    required_memory,
    duration,
    submit_time,
    priority,
    deadline
)
VALUES (?, ?, ?, ?, ?, ?, ?)
```

保存仿真结果时：

```sql
INSERT INTO simulations (
    algorithm,
    max_time,
    timeline_json,
    resource_history_json,
    metrics_json
)
VALUES (?, ?, ?, ?, ?)
```

### 3. 查询数据：`SELECT`
列出物理机：

```sql
SELECT id, name, total_cpu, total_memory, enabled
FROM machines
ORDER BY id
```

列出任务：

```sql
SELECT id, name, required_cpu, required_memory, duration, submit_time, priority, deadline
FROM tasks
ORDER BY id
```

查询单条仿真记录：

```sql
SELECT id, algorithm, max_time, timeline_json, resource_history_json, metrics_json
FROM simulations
WHERE id = ?
```

这几个例子里可以学到：
- `SELECT`：选择哪些列
- `FROM`：从哪张表查
- `ORDER BY`：按什么顺序返回
- `WHERE`：按条件筛选

### 4. 删除数据：`DELETE`
删除物理机：

```sql
DELETE FROM machines WHERE id = ?
```

删除任务：

```sql
DELETE FROM tasks WHERE id = ?
```

### 5. 更新数据：`UPDATE`
更新物理机：

```sql
UPDATE machines
SET name = ?, total_cpu = ?, total_memory = ?, enabled = ?
WHERE id = ?
```

更新任务：

```sql
UPDATE tasks
SET name = ?, required_cpu = ?, required_memory = ?, duration = ?, submit_time = ?, priority = ?, deadline = ?
WHERE id = ?
```

这里可以重点学习：
- `UPDATE`：更新已有记录
- `SET`：指定要修改的列
- `WHERE`：限定修改哪一行
- 如果 `WHERE` 条件匹配不到记录，更新行数就是 `0`

测试里重置数据库时，也使用了 `DELETE`：

```sql
DELETE FROM simulations;
DELETE FROM tasks;
DELETE FROM machines;
```

## Python 与 SQL 的衔接方式
项目中数据库访问集中在：`backend/app/core/store.py`

典型流程是：
1. `get_connection()` 建立 SQLite 连接。
2. 调用 `connection.execute(...)` 执行 SQL。
3. 用 `fetchone()` 或 `fetchall()` 取结果。
4. 把查询结果转成 Pydantic schema 返回给 API 层。

例如：
- 数据库中的 `enabled` 保存为整数。
- 返回 API 时再转成 Python `bool`。

这一步能帮助你理解：
- 数据库存储格式
- Python 运行时对象
- API 响应模型

这三者通常不是完全一样的。

## 目前还没有实现的 SQL 操作
当前版本刻意保持最小实现，所以还没有：
- 多表 `JOIN`
- 聚合查询，例如 `COUNT`、`AVG`、`SUM`
- 索引 `CREATE INDEX`
- 事务封装和回滚控制

这些都很适合作为后续学习任务。

## 建议的学习顺序
如果你想结合这个项目学习 SQL，建议按下面顺序看：

1. 先看 `backend/app/core/database.py`
2. 再看 `backend/app/core/store.py`
3. 对照 API 路由看数据是怎么流动的
4. 手动执行几条 SQL，观察数据库内容变化

可以重点观察这些问题：
- 为什么 `enabled` 用整数而不是布尔？
- 为什么 `deadline` 可以是 `NULL`？
- 为什么 `simulations` 里有些字段先存 JSON？
- `INSERT` 后为什么能通过 `lastrowid` 拿到主键？

## 后续可以练习的内容
如果继续拿这个项目练 SQL，可以从这些小功能开始：

1. 给 machines 增加更新接口，练习 `UPDATE`
2. 给 tasks 增加按提交时间排序查询
3. 增加统计接口，练习 `COUNT(*)`
4. 给常查字段建立索引，观察查询方式变化
5. 把仿真结果拆表，练习更规范的关系型设计
