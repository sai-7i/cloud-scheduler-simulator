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
- CPU 数值单位为“核”，内存数值单位为“MB”
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
    "total_memory": 8192,
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
  "total_memory": 8192,
  "enabled": true
}
```

响应示例：

```json
{
  "id": 1,
  "name": "node-a",
  "total_cpu": 4,
  "total_memory": 8192,
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
  "total_memory": 12288,
  "enabled": false
}
```

响应示例：

```json
{
  "id": 1,
  "name": "node-a-updated",
  "total_cpu": 6,
  "total_memory": 12288,
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
    "total_memory": 8192,
    "enabled": true
  },
  {
    "name": "node-b",
    "total_cpu": 6,
    "total_memory": 12288,
    "enabled": true
  }
]
```

### `POST /api/machines/import-sample`

从 `data/` 中导入示例物理机数据。导入前会先清空当前已有物理机，因此该接口是覆盖式导入。

这个接口不需要请求体。

可选查询参数：
- `dataset=default`
- `dataset=balanced`
- `dataset=stress`
- `dataset=fragmented`
- `dataset=priority`
- `dataset=deadline`
- `dataset=burst`

响应示例：

```json
[
  {
    "id": 1,
    "name": "node-a",
    "total_cpu": 4,
    "total_memory": 8192,
    "enabled": true
  },
  {
    "id": 2,
    "name": "node-b",
    "total_cpu": 6,
    "total_memory": 12288,
    "enabled": true
  }
]
```

### `DELETE /api/machines`

清空当前所有物理机配置。

成功响应：

```json
{
  "deleted_count": 4
}
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
    "required_memory": 4096,
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
  "required_memory": 4096,
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
  "required_memory": 4096,
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
  "required_memory": 6144,
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
  "required_memory": 6144,
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

从 `data/` 中导入示例任务数据。导入前会先清空当前已有任务，因此该接口是覆盖式导入。

这个接口不需要请求体。

可选查询参数：
- `dataset=default`
- `dataset=balanced`
- `dataset=stress`
- `dataset=fragmented`
- `dataset=priority`
- `dataset=deadline`
- `dataset=burst`

响应示例：

```json
[
  {
    "id": 1,
    "name": "task-1",
    "required_cpu": 2,
    "required_memory": 4096,
    "duration": 5,
    "submit_time": 0,
    "priority": 1,
    "deadline": 12
  }
]
```

### `DELETE /api/tasks`

清空当前所有任务配置。

成功响应：

```json
{
  "deleted_count": 8
}
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
- 返回本次仿真的算法名
- 返回完整时间线 `timeline`
- 返回资源历史 `resource_history`
- 返回指标 `metrics`
- 仿真结果不写入数据库历史记录

响应示例：

```json
{
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
    "average_waiting_time": 0.0,
    "max_waiting_time": 0,
    "average_turnaround_time": 5.0,
    "deadline_miss_rate": 0.0,
    "load_balance_score": 0.0,
    "average_cpu_load_balance_score": 0.0,
    "average_memory_load_balance_score": 0.0
  }
}
```

如果算法不支持，返回类似：

```json
{
  "detail": "Unsupported scheduler: unknown_algorithm"
}
```

### `POST /api/simulations/compare`

使用当前数据库中的物理机和任务配置，对多个算法分别运行仿真并返回对比结果。

请求示例：

```json
{
  "algorithms": ["first_fit", "least_loaded", "cfs_like"],
  "max_time": 20
}
```

响应示例：

```json
{
  "max_time": 20,
  "algorithms": ["first_fit", "least_loaded", "cfs_like"],
  "results": [
    {
      "algorithm": "first_fit",
      "timeline": [],
      "resource_history": [],
      "metrics": {
        "success_rate": 1.0,
        "rejection_rate": 0.0,
        "makespan": 5,
        "average_waiting_time": 0.0,
        "max_waiting_time": 0,
        "deadline_miss_rate": 0.0,
        "average_cpu_load_balance_score": 0.0,
        "average_memory_load_balance_score": 0.0
      }
    }
  ]
}
```

常用指标含义：

- `average_waiting_time`：完成任务的平均等待时间。
- `max_waiting_time`：完成任务中的最长等待时间。
- `deadline_miss_rate`：设置了截止期的任务中，完成时间超过截止期的比例。
- `load_balance_score`：仿真结束时各机器 CPU 利用率方差。
- `average_cpu_load_balance_score`：所有时间片的 CPU 利用率方差平均值，越低表示过程越均衡。
- `average_memory_load_balance_score`：所有时间片的内存利用率方差平均值，越低表示过程越均衡。

如果算法不支持，返回类似：

```json
{
  "detail": "Unsupported scheduler: unknown_algorithm"
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
