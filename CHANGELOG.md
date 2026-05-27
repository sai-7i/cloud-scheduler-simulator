# 变更日志

本文档记录项目各版本的重要发布内容。

## v1.0.0

发布日期：2026-05-15

### 版本定位

这是项目的第一个可发布版本，目标是交付一个可运行、可演示、可用于教学的云数据中心资源调度模拟器 MVP。

当前版本聚焦：
- CPU 与内存双资源调度
- 物理机与任务配置管理
- 离散时间仿真
- 基础算法对比
- 中文前端展示与图表分析

### 新增内容

#### 后端
- 新增 FastAPI 后端服务。
- 新增健康检查接口：`GET /health`。
- 新增物理机、任务、仿真三类 API。
- 新增 SQLite 持久化。
- 使用 Python 内置 `sqlite3` 和原生 SQL 实现数据访问。
- 机器和任务配置使用 SQLite 持久化；仿真结果不保存历史记录。

#### 仿真核心
- 新增物理机领域对象与任务领域对象。
- 新增集群资源分配与释放逻辑。
- 新增离散时间仿真引擎。
- 新增指标计算逻辑。

#### 已支持调度算法
- `first_fit`
- `best_fit`
- `worst_fit`
- `round_robin`
- `least_loaded`
- `cfs_like`

#### 前端
- 新增 Vue 3 前端界面。
- 新增物理机配置页面。
- 新增任务配置页面。
- 新增仿真运行页面。
- 新增概览页面。
- 新增指标卡片、资源利用率图表和任务时间线图。
- 新增物理机与任务的前端编辑能力。
- 新增算法对比页面。

#### 示例数据与演示支持
- 新增 `data/sample_machines.json`。
- 新增 `data/sample_tasks.json`。
- 新增示例物理机导入接口：`POST /api/machines/import-sample`。
- 新增示例任务导入接口：`POST /api/tasks/import-sample`。
- 新增内置演示任务生成接口：`POST /api/tasks/generate`。

#### 文档
- 新增 `README.md`。
- 新增架构说明：`docs/architecture.md`。
- 新增 API 文档：`docs/api.md`。
- 新增算法文档：`docs/algorithms.md`。
- 新增数据库文档：`docs/database.md`。

### 本版本支持的主要接口

#### 物理机
- `GET /api/machines`
- `POST /api/machines`
- `PUT /api/machines/{id}`
- `POST /api/machines/batch`
- `POST /api/machines/import-sample`
- `DELETE /api/machines/{id}`

#### 任务
- `GET /api/tasks`
- `POST /api/tasks`
- `PUT /api/tasks/{id}`
- `POST /api/tasks/generate`
- `POST /api/tasks/import-sample`
- `DELETE /api/tasks/{id}`

#### 仿真
- `POST /api/simulations/run`
- `POST /api/simulations/compare`

### 已完成验证

发布前已完成以下验证：
- 后端测试通过
- 前端生产构建通过：`npm run build`
- 健康检查接口可用
- 示例物理机导入可用
- 示例任务导入可用
- 以下 6 个算法都已通过真实 HTTP 仿真验证：
  - `first_fit`
  - `best_fit`
  - `worst_fit`
  - `round_robin`
  - `least_loaded`
  - `cfs_like`

### 已知限制

当前版本仍然有以下边界：
- 只建模 CPU 和内存，不包含磁盘和网络带宽。
- 不支持抢占式调度。
- 不支持任务迁移。
- 不支持物理机故障与恢复。
- 不支持自动扩缩容。
- 不支持多租户公平性。
- 不包含遗传算法、强化学习或更复杂的优化算法。

此外需要注意：
- `cfs_like` 是教学用简化实现，不是 Linux CFS 的完整实现。
- `least_loaded` 当前采用“CPU 利用率优先，内存利用率次之”的简化负载定义。
- 仿真结果只在本次 API 响应和当前前端页面中展示，不保存历史记录。

### 升级建议

后续版本建议优先考虑：
- `priority`、`sjf`、`edf` 等队列选择策略。
- 更完整的多维资源均衡策略。
- 导出仿真结果或设计可选的实验归档能力。
- 启动脚本、Docker 或部署支持。

## v1.0.2

发布日期：2026-05-27

### 版本定位

本次更新新增一键启动脚本，简化项目启动流程，提升用户体验。

当前版本聚焦：
- 跨平台启动脚本支持
- 自动依赖安装
- 一键式服务管理

### 新增内容

#### 启动脚本
- 新增 Windows 一键启动脚本：`start.bat`。
- 新增 Linux/macOS 一键启动脚本：`start.sh`。
- 支持首次运行自动安装 Python 虚拟环境和后端依赖。
- 支持首次运行自动安装前端 npm 依赖。
- 支持同时启动后端（端口 8000）和前端（端口 5173）服务。
- 支持 `Ctrl+C` 优雅停止所有服务。
- 使用标记文件记录依赖安装状态，后续运行跳过安装。

#### 文档更新
- 更新 `README.md`：新增一键启动说明和功能清单。
- 更新 `AGENTS.md`：添加启动脚本到目录结构说明。
- 更新 `CHANGELOG.md`：记录 v1.0.2 版本变更内容。

### 已完成验证

发布前已完成以下验证：
- Windows 启动脚本创建成功
- Linux/macOS 启动脚本创建成功并添加执行权限
- 脚本语法检查通过
- 文档更新完成

### 使用说明

**Windows：**
```bash
start.bat
```

**Linux/macOS：**
```bash
./start.sh
```

脚本会自动检测并安装缺失的依赖，然后同时启动前后端服务。
