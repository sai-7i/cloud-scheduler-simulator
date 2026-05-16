# 任务清单

## 当前阶段
初始化一个紧凑、可运行的 MVP 骨架，覆盖后端、前端、仿真、测试和文档。

## 第 1 步：文档
- 创建根目录 `README.md`。
- 创建 `docs/architecture.md`。
- 创建 `docs/api.md`。
- 创建 `docs/algorithms.md`。
- 创建 `docs/tasks.md`。

验证方式：
- 文件存在，并且内容与 `AGENTS.md` 中的技术栈和范围一致。

## 第 2 步：后端骨架
- 添加 `backend/requirements.txt`，使用当前 Python 版本可安装的最新兼容依赖。
- 添加 `backend/app/main.py`，暴露 `app = FastAPI()`。
- 在需要的位置添加包初始化文件 `__init__.py`。
- 添加健康检查路由，用于导入和服务检查。

验证方式：
- `cd backend && python -c "from app.main import app; print(app.title)"` 能成功执行。
- Python 3.14 环境应使用 Pydantic v2；不要使用 Pydantic v1。

## 第 3 步：仿真核心
- 添加物理机和任务的纯 Python 领域对象。
- 添加集群资源分配和释放行为。
- 添加离散时间仿真引擎。
- 添加指标计算。

验证方式：
- 不启动 Web 服务的情况下，聚焦的后端测试可以通过。

## 第 4 步：调度器
- 实现 `first_fit`。
- 实现 `best_fit`。
- 实现 `worst_fit`。
- 实现 `round_robin`。

验证方式：
- 确定性的调度器测试可以通过。

## 第 5 步：API 层
- 添加物理机路由。
- 添加任务路由。
- 添加仿真路由。
- 在核心行为验证前，持久化保持最小化。

验证方式：
- FastAPI 应用能导入，并且路由列表包含 `/api` 接口。

## 第 6 步：持久化
- 添加基于 `sqlite3` 的 SQLite 配置。
- 使用原生 SQL 完成物理机和任务配置持久化；仿真结果只在本次响应中返回。
- 除非明确要求，不要提交生成的 `.db` 文件。

验证方式：
- 数据库配置可以成功导入。

## 第 7 步：前端骨架
- 添加 Vite/Vue 项目文件。
- 添加 Vue Router。
- 添加 Axios API 封装。
- 添加物理机配置、任务配置、仿真运行、结果分析页面。
- 添加可复用表格、指标卡片、资源图表和时间线占位组件。

验证方式：
- 安装依赖后，`cd frontend && npm install && npm run build` 能成功执行。

## 第 8 步：示例数据
- 添加物理机/任务 JSON 示例数据，用于演示。
- 保持运行时 SQLite 数据库文件不进入源码。

验证方式：
- 示例数据可以被测试或演示脚本使用。

## 第 9 步：最终 MVP 检查
- 后端测试通过。
- 后端可以成功导入。
- 前端可以构建。
- README 中的命令与实际文件一致。
