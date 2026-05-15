# API 说明

所有 API 都挂载在 `/api` 前缀下。

当前系统主要分为三组接口：
- 物理机接口
- 任务接口
- 仿真接口

## 通用说明

- 后端默认运行地址：`http://127.0.0.1:8000`
- 前端开发环境通过 Vite 代理访问 `/api`
- 当前响应格式以 JSON 为主
- 如果请求的资源不存在，接口通常返回 `404`
- 如果请求参数非法或算法名不支持，接口可能返回 `400`

## 物理机

### `GET /api/machines`

返回当前所有物理机配置。

响应示例：

```json
[
  {
    "id": 1,
    "name": "node-a",
    "total_cpu": 4,
    "total_memory": 8,
    "enabled": true
  }
]
```

### `POST /api/machines`

创建一台物理机。

请求示例：

```json
{
  "name": "node-a",
  "total_cpu": 4,
  "total_memory": 8,
  "enabled": true
}
```

响应示例：

```json
{
  "id": 1,
  "name": "node-a",
  "total_cpu": 4,
  "total_memory": 8,
  "enabled": true
}
```

### `PUT /api/machines/{id}`

更新一台已存在的物理机。

请求示例：

```json
{
  "name": "node-a-updated",
  "total_cpu": 6,
  "total_memory": 12,
  "enabled": false
}
```

响应示例：

```json
{
  "id": 1,
  "name": "node-a-updated",
  "total_cpu": 6,
  "total_memory": 12,
  "enabled": false
}
```

如果 `id` 不存在，返回：

```json
{
  "detail": "Machine not found"
}
```

### `POST /api/machines/batch`

批量创建物理机，适合初始化演示数据。

请求示例：

```json
[
  {
    "name": "node-a",
    "total_cpu": 4,
    "total_memory": 8,
    "enabled": true
  },
  {
    "name": "node-b",
    "total_cpu": 6,
    "total_memory": 12,
    "enabled": true
  }
]
```

### `POST /api/machines/import-sample`

从 `data/sample_machines.json` 导入示例物理机数据。

这个接口不需要请求体。

可选查询参数：
- `dataset=default`
- `dataset=balanced`
- `dataset=stress`

响应示例：

```json
[
  {
    "id": 1,
    "name": "node-a",
    "total_cpu": 4,
    "total_memory": 8,
    "enabled": true
  },
  {
    "id": 2,
    "name": "node-b",
    "total_cpu": 6,
    "total_memory": 12,
    "enabled": true
  }
]
```

### `DELETE /api/machines/{id}`

删除一台物理机。

成功响应：

```json
{
  "deleted": true
}
```

如果 `id` 不存在，返回：

```json
{
  "detail": "Machine not found"
}
```

## 任务

### `GET /api/tasks`

返回当前所有任务配置。

响应示例：

```json
[
  {
    "id": 1,
    "name": "task-1",
    "required_cpu": 2,
    "required_memory": 4,
    "duration": 5,
    "submit_time": 0,
    "priority": 1,
    "deadline": 12
  }
]
```

### `POST /api/tasks`

创建一个任务。

请求示例：

```json
{
  "name": "task-1",
  "required_cpu": 2,
  "required_memory": 4,
  "duration": 5,
  "submit_time": 0,
  "priority": 1,
  "deadline": 12
}
```

响应示例：

```json
{
  "id": 1,
  "name": "task-1",
  "required_cpu": 2,
  "required_memory": 4,
  "duration": 5,
  "submit_time": 0,
  "priority": 1,
  "deadline": 12
}
```

### `PUT /api/tasks/{id}`

更新一个已存在的任务。

请求示例：

```json
{
  "name": "task-1-updated",
  "required_cpu": 3,
  "required_memory": 6,
  "duration": 7,
  "submit_time": 1,
  "priority": 2,
  "deadline": 20
}
```

响应示例：

```json
{
  "id": 1,
  "name": "task-1-updated",
  "required_cpu": 3,
  "required_memory": 6,
  "duration": 7,
  "submit_time": 1,
  "priority": 2,
  "deadline": 20
}
```

如果 `id` 不存在，返回：

```json
{
  "detail": "Task not found"
}
```

### `POST /api/tasks/generate`

生成一组内置演示任务。

这个接口不需要请求体。

说明：
- 这是后端写死的一小组演示任务。
- 适合快速联调和演示基础流程。

### `POST /api/tasks/import-sample`

从 `data/sample_tasks.json` 导入示例任务数据。

这个接口不需要请求体。

可选查询参数：
- `dataset=default`
- `dataset=balanced`
- `dataset=stress`

响应示例：

```json
[
  {
    "id": 1,
    "name": "task-1",
    "required_cpu": 2,
    "required_memory": 4,
    "duration": 5,
    "submit_time": 0,
    "priority": 1,
    "deadline": 12
  }
]
```

### `DELETE /api/tasks/{id}`

删除一个任务。

成功响应：

```json
{
  "deleted": true
}
```

如果 `id` 不存在，返回：

```json
{
  "detail": "Task not found"
}
```

## 仿真

### `POST /api/simulations/run`

使用当前数据库中的物理机和任务配置，运行一次仿真。

请求示例：

```json
{
  "algorithm": "first_fit",
  "max_time": 20
}
```

响应说明：
- 返回新生成的仿真记录 ID
- 返回本次仿真的算法名
- 返回完整时间线 `timeline`
- 返回资源历史 `resource_history`
- 返回指标 `metrics`

响应示例：

```json
{
  "id": 1,
  "algorithm": "first_fit",
  "timeline": [
    {
      "task_id": 1,
      "task_name": "task-1",
      "machine_name": "node-a",
      "start_time": 0,
      "finish_time": 5
    }
  ],
  "resource_history": [],
  "metrics": {
    "success_rate": 1.0,
    "rejection_rate": 0.0,
    "makespan": 5,
    "average_waiting_time": 0.0
  }
}
```

如果算法不支持，返回类似：

```json
{
  "detail": "Unsupported scheduler: unknown_algorithm"
}
```

### `GET /api/simulations/latest`

返回最近一次仿真的完整结果。

返回内容包含：
- `id`
- `algorithm`
- `max_time`
- `timeline`
- `resource_history`
- `metrics`

如果当前还没有任何仿真记录，返回：

```json
{
  "detail": "Simulation not found"
}
```

### `GET /api/simulations/{id}`

返回某次仿真的基础元数据。

响应示例：

```json
{
  "id": 1,
  "algorithm": "first_fit",
  "max_time": 20
}
```

### `GET /api/simulations/{id}/results`

返回某次仿真的详细结果：
- `timeline`
- `resource_history`

### `GET /api/simulations/{id}/metrics`

返回某次仿真的最终指标。

常见字段包括：
- `average_cpu_utilization`
- `average_memory_utilization`
- `average_waiting_time`
- `average_turnaround_time`
- `success_rate`
- `rejection_rate`
- `makespan`
- `load_balance_score`

如果仿真 `id` 不存在，上述三个查询接口都会返回：

```json
{
  "detail": "Simulation not found"
}
```

## 算法名称

当前后端真正支持以下算法名：

- `first_fit`
- `best_fit`
- `worst_fit`
- `round_robin`
- `least_loaded`
- `cfs_like`

其他算法如 `priority`、`sjf`、`edf`、`balanced`、`quota_aware` 目前仍处于设计阶段，尚未开放为可运行 API 参数。
