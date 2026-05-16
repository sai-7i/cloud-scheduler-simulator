# 云数据中心资源调度模拟器

一个面向教学、课程演示和调度算法实验的小型云数据中心资源调度模拟器。

第一版聚焦 CPU 和内存两个资源维度，提供物理机配置、任务配置、调度算法选择、算法对比、离散时间仿真、指标统计和图表展示能力。项目采用前后端分离结构，后端使用 FastAPI，前端使用 Vue 3，机器与任务配置使用 SQLite 和原生 SQL 持久化。

## 当前版本

- 版本目标：`v1.0.0` MVP
- 当前状态：第一版功能已完成，可用于本地运行、课程演示和算法对比实验

## 功能清单

当前版本已支持：

- 物理机管理
  - 新增物理机
  - 编辑物理机
  - 删除物理机
  - 批量导入示例物理机
- 任务管理
  - 新增任务
  - 编辑任务
  - 删除任务
  - 生成演示任务
  - 导入示例任务
- 仿真运行
  - 选择调度算法
  - 设置最大仿真时间
  - 运行仿真
  - 在当前页面查看本次仿真结果
- 算法对比
  - 一次选择多个算法
  - 使用同一组机器和任务横向对比指标
  - 展示对比图表和结果表格
- 结果分析
  - 指标卡片
  - 资源利用率趋势图
  - 任务时间线图
- 数据持久化
  - 机器配置持久化
  - 任务配置持久化
  - 仿真结果不持久化，刷新页面后不保留

## 当前支持的调度算法

当前后端可直接运行以下算法：

- `first_fit`
- `best_fit`
- `worst_fit`
- `round_robin`
- `least_loaded`
- `cfs_like`

这些算法的详细说明见：`docs/algorithms.md`

## 技术栈

- 后端：Python、FastAPI、Uvicorn
- 数据库：SQLite、Python 内置 `sqlite3`、原生 SQL
- 数据校验：Pydantic v2
- 前端：Vue 3、Vue Router、Axios
- 图表：ECharts

## 本地服务地址

- 后端：`http://127.0.0.1:8000`
- 前端：`http://127.0.0.1:5173`

## 目录结构

- `backend/`：FastAPI API、仿真核心、调度器、SQLite 持久化、测试
- `frontend/`：Vue UI、路由、API 客户端、图表组件、页面
- `docs/`：架构、API、算法、数据库和任务文档
- `data/`：本地数据库和示例数据
- `scripts/`：预留给启动或辅助脚本

## 快速开始

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

说明：
- 当前开发环境使用 Python 3.14。
- 当前项目使用 Pydantic v2，不要回退到 Pydantic v1。
- 后端健康检查地址：`GET /health`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器会通过 Vite 代理访问后端 `/api`。

### 3. 运行测试

后端测试：

```bash
cd backend
.venv/bin/pytest
```

### 4. 前端构建

```bash
cd frontend
npm run build
```

## 演示流程

推荐用下面的顺序进行完整演示：

1. 启动后端和前端服务。
2. 打开前端页面。
3. 进入“物理机”页面，点击“导入示例数据”。
4. 进入“任务”页面，点击“导入示例任务”。
5. 进入“仿真”页面，选择一种算法并设置最大仿真时间。
6. 点击“开始运行”。
7. 查看指标卡、资源利用率趋势图和任务时间线图。
8. 进入“算法对比”页面，选择多个算法并查看横向对比结果。

你也可以手动创建机器和任务，而不使用示例数据。

## 示例数据

项目中 CPU 使用“核”作为单位，内存使用“MB”作为单位。示例数据已按 MB 级别编排，例如 4 核任务通常对应 4096 MB、8192 MB 等更合理的内存需求。

当前仓库已包含默认示例数据：

- `data/sample_machines.json`
- `data/sample_tasks.json`

此外还提供额外测试集：

- `balanced`：更适合观察均衡调度行为
- `stress`：更适合观察高压力负载下的调度差异
- `fragmented`：更适合观察 CPU/内存资源碎片和紧凑/分散放置差异
- `priority`：更适合观察长任务与高优先级短任务竞争时的等待差异
- `deadline`：更适合观察截止期违约率和紧迫任务完成情况
- `burst`：更适合观察多波次突发提交下的排队与负载均衡

这些数据包含更明显的异构机器、CPU 密集型任务、内存密集型任务、短任务、长任务、不同优先级和不同截止期，用于让不同算法在等待时间、截止期违约率和负载均衡分数上产生更直观的差异。

对应导入接口：

- `POST /api/machines/import-sample`
- `POST /api/tasks/import-sample`

导入测试集时会先清空对应类型的已有配置，再写入所选测试集，避免多次导入导致数据叠加。
如果需要手动清空，也可以使用：

- `DELETE /api/machines`
- `DELETE /api/tasks`

可通过 `dataset` 参数手动选择测试集，例如：

- `POST /api/machines/import-sample?dataset=default`
- `POST /api/machines/import-sample?dataset=balanced`
- `POST /api/machines/import-sample?dataset=stress`
- `POST /api/machines/import-sample?dataset=fragmented`
- `POST /api/machines/import-sample?dataset=priority`
- `POST /api/machines/import-sample?dataset=deadline`
- `POST /api/machines/import-sample?dataset=burst`
- `POST /api/tasks/import-sample?dataset=default`
- `POST /api/tasks/import-sample?dataset=balanced`
- `POST /api/tasks/import-sample?dataset=stress`
- `POST /api/tasks/import-sample?dataset=fragmented`
- `POST /api/tasks/import-sample?dataset=priority`
- `POST /api/tasks/import-sample?dataset=deadline`
- `POST /api/tasks/import-sample?dataset=burst`

## 数据库说明

- 默认数据库文件：`data/simulator.db`
- 测试数据库文件：`backend/tests/test.db`
- 可通过环境变量 `APP_DB_PATH` 覆盖数据库路径

数据库表结构、原生 SQL 示例和设计说明见：`docs/database.md`

## 文档索引

- 架构说明：`docs/architecture.md`
- API 说明：`docs/api.md`
- 算法说明：`docs/algorithms.md`
- 数据库说明：`docs/database.md`
- 开发任务清单：`docs/tasks.md`

## 当前已知限制

第一版有意保持紧凑，当前不包含以下能力：

- 磁盘与网络带宽建模
- 抢占式调度
- 任务迁移
- 物理机故障与恢复
- 自动扩缩容
- 多租户公平性
- 高级资源隔离策略
- 遗传算法与强化学习算法

此外，当前版本中的：

- `cfs_like` 是教学用简化实现，不是 Linux CFS 的完整复刻
- `least_loaded` 当前使用“CPU 利用率优先、内存利用率次之”的简化负载定义
- 仿真结果只在本次 API 响应和当前前端页面中展示，不写入数据库历史记录

## 发布前验证结果

当前版本已经完成以下验证：

- 后端测试通过
- 前端构建通过
- 示例数据可导入
- 已支持算法可在前端运行
- 算法对比页面可构建

## 许可证与说明

当前仓库主要用于教学、课程设计与演示。如需继续扩展，建议从 `docs/algorithms.md` 和 `docs/architecture.md` 开始阅读。
