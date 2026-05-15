# 架构说明

## 目标
构建一个小型模拟器，用于演示不同调度算法如何把虚拟任务放置到物理机上。

## 运行形态
- 后端使用 FastAPI 暴露 REST API。
- 仿真核心使用纯 Python 实现，可以在不启动 HTTP、SQLite 或前端的情况下测试。
- 核心行为跑通后，SQLite 通过 Python 内置 `sqlite3` 和原生 SQL 保存机器配置、任务配置、仿真运行、结果和指标。
- Vue 前端通过 Axios 调用后端，展示配置表单、任务列表、图表、时间线和指标卡片。

## 后端边界
- `app/main.py`：创建 FastAPI 应用并挂载 API 路由。
- `app/api/`：只放 HTTP 路由；不要把调度逻辑写进路由函数。
- `app/core/database.py`：SQLite 连接和建表逻辑。
- `app/core/store.py`：原生 SQL 数据访问函数。
- `app/schemas/`：Pydantic 请求/响应模型。
- `app/simulation/`：领域对象、集群状态、离散时间仿真引擎和指标计算。
- `app/schedulers/`：机器放置算法。

## 仿真流程
1. 加载或接收物理机和任务输入。
2. 按提交时间排序任务。
3. 按离散时间 tick 推进仿真。
4. 将当前时间新提交的任务加入等待队列。
5. 释放已完成任务并归还机器资源。
6. 调用选定调度器放置等待任务。
7. 记录当前 tick 的每台机器 CPU 和内存使用情况。
8. 当所有任务完成或达到最大仿真时间时停止。
9. 返回任务时间线、资源历史和统计指标。

## 前端页面
- 物理机配置：创建/删除物理机并查看容量。
- 任务配置：创建/删除任务并生成示例负载。
- 仿真运行：选择算法和最大仿真时间，然后启动仿真。
- 结果分析：展示指标、资源利用率图表和任务时间线。

## 前端打包说明
- 图表组件 `EChartPanel.vue` 仍然作为异步组件按需加载，避免非图表页面首屏加载 ECharts。
- 由于 ECharts 和 `zrender` 体积较大，前端在 `vite.config.js` 中使用了 `build.rollupOptions.output.manualChunks` 进一步拆包。
- 当前拆分出的主要前端图表相关 chunk 包括：
  - `echarts-core`
  - `echarts-charts`
  - `echarts-components`
  - `echarts-renderers`
  - `zrender`
- 这样做的原因是：
  - 避免单个 ECharts 异步包超过 500 kB 并触发构建 warning。
  - 让图表依赖按模块切分，减少单块体积。
  - 保持图表相关代码只在需要时加载。
- 本地构建验证后，原先超过 500 kB 的单个 ECharts chunk 已被拆散，构建 warning 已消失。

## 数据范围
MVP 只建模 CPU 和内存。磁盘、网络带宽、迁移、物理机故障、自动扩缩容、多租户公平性、遗传算法和强化学习都不在第一版范围内。

数据库表结构和当前原生 SQL 示例见 `docs/database.md`。
