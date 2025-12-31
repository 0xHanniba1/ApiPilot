# ApiPilot 开发者文档

本文档面向开发者，介绍如何参与 ApiPilot 项目的开发。

## 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目架构](#项目架构)
3. [后端开发](#后端开发)
4. [前端开发](#前端开发)
5. [数据库设计](#数据库设计)
6. [API 设计规范](#api-设计规范)
7. [测试](#测试)
8. [部署](#部署)

---

## 开发环境搭建

### 系统要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (可选)

### 后端环境

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 开发环境

使用 Docker Compose 快速启动依赖服务：

```bash
# 仅启动数据库和 Redis
docker compose up -d postgres redis

# 或启动全部服务
docker compose up -d
```

---

## 项目架构

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                      Nginx                          │
│              (反向代理 / 静态文件托管)                 │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   Frontend    │               │   Backend     │
│   (Vue 3)     │               │   (FastAPI)   │
└───────────────┘               └───────┬───────┘
                                        │
                ┌───────────────────────┼───────────────────────┐
                │                       │                       │
                ▼                       ▼                       ▼
        ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
        │  PostgreSQL   │       │     Redis     │       │    Celery     │
        │   (数据存储)   │       │  (缓存/队列)   │       │   (异步任务)   │
        └───────────────┘       └───────────────┘       └───────────────┘
```

### 后端目录结构

```
backend/
├── app/
│   ├── api/                    # API 路由层
│   │   └── v1/
│   │       ├── projects.py     # 项目相关 API
│   │       ├── environments.py # 环境相关 API
│   │       ├── modules.py      # 模块相关 API
│   │       ├── cases.py        # 用例相关 API
│   │       ├── suites.py       # 测试集相关 API
│   │       ├── executions.py   # 执行相关 API
│   │       ├── schedules.py    # 定时任务 API
│   │       └── stats.py        # 统计相关 API
│   │
│   ├── models/                 # 数据模型层 (SQLAlchemy)
│   │   ├── project.py
│   │   ├── environment.py
│   │   ├── module.py
│   │   ├── test_case.py
│   │   ├── test_suite.py
│   │   ├── execution.py
│   │   └── schedule.py
│   │
│   ├── schemas/                # 数据验证层 (Pydantic)
│   │   ├── project.py
│   │   ├── environment.py
│   │   ├── test_case.py
│   │   ├── execution.py
│   │   └── schedule.py
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── executor.py         # 用例执行器
│   │   ├── assertion.py        # 断言处理
│   │   └── extractor.py        # 变量提取
│   │
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   └── database.py         # 数据库连接
│   │
│   └── main.py                 # 应用入口
│
├── celery_app/                 # Celery 配置
│   ├── celery.py               # Celery 实例
│   └── tasks.py                # 异步任务
│
├── alembic/                    # 数据库迁移
│   ├── versions/               # 迁移脚本
│   └── env.py
│
├── tests/                      # 测试代码
├── requirements.txt            # Python 依赖
└── Dockerfile                  # Docker 构建
```

### 前端目录结构

```
frontend/
├── src/
│   ├── api/                    # API 调用封装
│   │   ├── index.js            # Axios 实例
│   │   ├── project.js
│   │   ├── case.js
│   │   ├── suite.js
│   │   ├── execution.js
│   │   ├── schedule.js
│   │   └── stats.js
│   │
│   ├── views/                  # 页面组件
│   │   ├── Dashboard.vue       # 首页
│   │   ├── Layout.vue          # 布局
│   │   ├── project/            # 项目相关页面
│   │   ├── case/               # 用例相关页面
│   │   ├── suite/              # 测试集页面
│   │   ├── execution/          # 执行相关页面
│   │   └── schedule/           # 定时任务页面
│   │
│   ├── router/                 # 路由配置
│   │   └── index.js
│   │
│   ├── assets/                 # 静态资源
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
│
├── public/                     # 公共资源
├── nginx.conf                  # Nginx 配置
├── Dockerfile                  # Docker 构建
├── package.json
└── vite.config.js
```

---

## 后端开发

### 技术栈

- **FastAPI**: 异步 Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **Pydantic**: 数据验证
- **Alembic**: 数据库迁移
- **Celery**: 异步任务队列
- **HTTPX**: 异步 HTTP 客户端

### 添加新的 API

1. **定义数据模型** (`app/models/`)

```python
# app/models/example.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

2. **定义 Schema** (`app/schemas/`)

```python
# app/schemas/example.py
from pydantic import BaseModel, Field
from datetime import datetime

class ExampleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)

class ExampleResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

3. **创建 API 路由** (`app/api/v1/`)

```python
# app/api/v1/examples.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.example import ExampleCreate, ExampleResponse
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/examples", tags=["Examples"])

@router.post("", response_model=ResponseModel)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db)
):
    # 业务逻辑
    return {"code": 0, "message": "success", "data": result}
```

4. **注册路由** (`app/main.py`)

```python
from app.api.v1.examples import router as examples_router
app.include_router(examples_router, prefix="/api/v1")
```

5. **创建数据库迁移**

```bash
alembic revision --autogenerate -m "add examples table"
alembic upgrade head
```

### 异步任务

使用 Celery 处理耗时操作：

```python
# celery_app/tasks.py
from celery_app.celery import celery

@celery.task
def execute_test_suite(suite_id: int, environment_id: int):
    # 执行测试集
    pass
```

调用异步任务：

```python
from celery_app.tasks import execute_test_suite
execute_test_suite.delay(suite_id=1, environment_id=1)
```

---

## 前端开发

### 技术栈

- **Vue 3**: 组合式 API
- **Element Plus**: UI 组件库
- **Vue Router**: 路由管理
- **ECharts**: 图表可视化
- **Monaco Editor**: 代码编辑器
- **Axios**: HTTP 客户端

### 添加新页面

1. **创建页面组件** (`src/views/`)

```vue
<!-- src/views/example/ExampleList.vue -->
<template>
  <div class="example-list">
    <div class="page-header">
      <h2 class="page-title">示例列表</h2>
      <el-button type="primary" @click="handleCreate">新建</el-button>
    </div>
    <el-table :data="list" v-loading="loading">
      <!-- 表格内容 -->
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getExamples } from '@/api/example'

const list = ref([])
const loading = ref(false)

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getExamples()
    list.value = res.data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchList)
</script>
```

2. **封装 API** (`src/api/`)

```javascript
// src/api/example.js
import request from './index'

export function getExamples(params) {
  return request.get('/examples', { params })
}

export function createExample(data) {
  return request.post('/examples', data)
}
```

3. **配置路由** (`src/router/index.js`)

```javascript
{
  path: 'examples',
  name: 'ExampleList',
  component: () => import('@/views/example/ExampleList.vue'),
  meta: { title: '示例列表', icon: 'Document' },
}
```

### 组件规范

- 使用 `<script setup>` 组合式 API
- Props 使用 defineProps 定义
- 事件使用 defineEmits 定义
- 样式使用 `<style lang="scss" scoped>`

---

## 数据库设计

### ER 图

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Project    │       │ Environment  │       │    Module    │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │◄──────┤ project_id   │       │ id           │
│ name         │       │ name         │       │ project_id   │──►
│ description  │       │ base_url     │       │ parent_id    │
│ created_at   │       │ is_default   │       │ name         │
└──────────────┘       └──────────────┘       └──────────────┘
        │                                            │
        │                                            │
        ▼                                            ▼
┌──────────────┐                             ┌──────────────┐
│  TestSuite   │                             │  TestCase    │
├──────────────┤                             ├──────────────┤
│ id           │                             │ id           │
│ project_id   │                             │ module_id    │
│ name         │                             │ name         │
│ exec_mode    │                             │ method       │
└──────────────┘                             │ path         │
        │                                    │ headers      │
        │                                    │ params       │
        ▼                                    │ body_type    │
┌──────────────┐                             └──────────────┘
│ SuiteCase    │                                    │
├──────────────┤          ┌─────────────────────────┤
│ suite_id     │          │                         │
│ case_id      │          ▼                         ▼
│ sort_order   │   ┌──────────────┐         ┌──────────────┐
└──────────────┘   │  Assertion   │         │  Extractor   │
                   ├──────────────┤         ├──────────────┤
                   │ case_id      │         │ case_id      │
                   │ type         │         │ source       │
                   │ expression   │         │ expression   │
                   │ operator     │         │ variable_name│
                   └──────────────┘         └──────────────┘
```

### 主要表说明

| 表名 | 说明 |
|------|------|
| projects | 项目信息 |
| environments | 环境配置 |
| modules | 模块（支持树形结构） |
| test_cases | 测试用例 |
| assertions | 断言配置 |
| extractors | 变量提取器 |
| test_suites | 测试集 |
| suite_cases | 测试集与用例关联 |
| executions | 执行记录 |
| execution_details | 执行详情 |
| schedules | 定时任务 |

---

## API 设计规范

### 响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误响应：
```json
{
  "code": 1001,
  "message": "参数错误",
  "data": null
}
```

### 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### URL 设计

| 操作 | 方法 | URL |
|------|------|-----|
| 列表 | GET | /api/v1/resources |
| 详情 | GET | /api/v1/resources/{id} |
| 创建 | POST | /api/v1/resources |
| 更新 | PUT | /api/v1/resources/{id} |
| 删除 | DELETE | /api/v1/resources/{id} |

### 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 资源不存在 |
| 1003 | 权限不足 |
| 2001 | 执行失败 |

---

## 测试

### 后端测试

```bash
cd backend
pytest tests/ -v
```

### 前端测试

```bash
cd frontend
npm run test
```

---

## 部署

### Docker 部署

```bash
# 构建并启动
docker compose up -d --build

# 仅构建
docker compose build

# 查看日志
docker compose logs -f
```

### 生产环境配置

1. 修改 `.env` 文件中的敏感配置
2. 配置 HTTPS（通过 Nginx 或负载均衡器）
3. 配置备份策略
4. 配置监控告警

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| POSTGRES_USER | 数据库用户 | apipilot |
| POSTGRES_PASSWORD | 数据库密码 | apipilot123 |
| POSTGRES_DB | 数据库名 | apipilot |
| REDIS_URL | Redis 地址 | redis://redis:6379/0 |
| APP_ENV | 运行环境 | production |
| APP_DEBUG | 调试模式 | false |

---

## 代码规范

### Python

- 遵循 PEP 8
- 使用 Type Hints
- 函数/方法添加文档字符串
- 异步函数使用 async/await

### JavaScript/Vue

- 使用 ESLint + Prettier
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case
- 使用组合式 API

---

如有问题，欢迎提交 Issue 或 Pull Request。
