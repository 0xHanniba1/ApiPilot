# ApiPilot

**ApiPilot** 是一个现代化的 API 自动化测试平台，提供完整的接口测试解决方案，包括用例管理、测试执行、定时任务和测试报告等功能。

## 特性

- **项目管理** - 支持多项目、多环境配置，灵活管理测试资源
- **用例编辑** - 可视化用例编辑器，支持变量提取、断言配置、前后置脚本
- **测试集** - 组织用例形成测试集，支持顺序/并行执行模式
- **定时任务** - Cron 表达式配置，支持可视化周期设置
- **执行报告** - 详细的执行日志、断言结果、响应数据展示
- **数据统计** - 执行趋势、通过率、失败率 Top5 等多维度分析

## 技术栈

### 后端
- **Python 3.11** + **FastAPI** - 高性能异步 API 框架
- **PostgreSQL** - 关系型数据库存储
- **Redis** - 缓存与消息队列
- **Celery** - 异步任务与定时调度
- **SQLAlchemy 2.0** - 异步 ORM
- **Alembic** - 数据库迁移

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - UI 组件库
- **ECharts** - 图表可视化
- **Monaco Editor** - 代码编辑器
- **Vite** - 构建工具

### 部署
- **Docker** + **Docker Compose** - 容器化部署
- **Nginx** - 反向代理与静态文件托管

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-org/apipilot.git
cd apipilot

# 2. 复制环境配置
cp .env.example .env

# 3. 启动服务
docker compose up -d

# 4. 访问应用
# 前端: http://localhost
# API 文档: http://localhost/docs
```

### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | 前端应用 (Nginx) |
| backend | 8000 | 后端 API |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |
| celery_worker | - | Celery 异步任务 |
| celery_beat | - | Celery 定时调度 |

### 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重新构建
docker compose up -d --build

# 停止服务
docker compose down

# 停止并清除数据
docker compose down -v
```

## 功能截图

### 首页仪表盘
统计卡片展示项目数、用例数、今日执行数和通过率；执行趋势图和今日统计饼图；最近执行记录和失败率 Top5 用例排行。

### 项目管理
项目列表支持搜索筛选；项目详情页包含环境配置、模块树和用例列表；支持多环境变量配置。

### 用例编辑
可视化请求配置（方法、路径、Headers、Params、Body）；断言配置支持状态码、JSON Path、响应时间等多种类型；变量提取器配置；前后置脚本支持。

### 测试集
测试集列表与详情；拖拽排序用例执行顺序；支持顺序/并行执行模式。

### 定时任务
任务列表管理；Cron 表达式可视化配置；通知配置（邮件、Webhook、钉钉、企业微信）；执行历史记录。

### 执行报告
执行概览（状态、通过率、耗时）；详细的断言结果展示；请求/响应详情查看。

## API 文档

启动服务后，可通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc
- **OpenAPI JSON**: http://localhost/openapi.json

## 目录结构

```
apipilot/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   └── core/           # 核心配置
│   ├── celery_app/         # Celery 配置
│   ├── alembic/            # 数据库迁移
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── assets/        # 静态资源
│   ├── nginx.conf         # Nginx 配置
│   └── Dockerfile
├── docs/                   # 文档
├── docker-compose.yml      # Docker 编排
└── README.md
```

## 开发指南

### 本地开发

```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端开发
cd frontend
npm install
npm run dev
```

### 数据库迁移

```bash
# 创建迁移
cd backend
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```

## 文档

- [用户使用手册](docs/user-guide.md)
- [开发者文档](docs/developer-guide.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
