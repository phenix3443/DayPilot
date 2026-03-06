# DayPilot MVP

AI 驱动的个人时间管理工具 - 最小可行产品

## 环境要求

- Python 3.11+
- Poetry (Python 包管理器)
- 浏览器（用于 Web UI）

## 安装步骤

### 1. 克隆仓库并安装依赖

```bash
cd apps/api
poetry install
```

### 2. 配置 API Key

创建 `.env` 文件（在项目根目录）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API key：

```
DEEPSEEK_API_KEY=your_api_key_here
```

**获取 API Key：**
- 当前使用 skyapi.org 服务
- 模型：claude-sonnet-4-6
- API 兼容 OpenAI 格式

### 3. 启动 API 服务器

```bash
cd apps/api
DEEPSEEK_API_KEY=<your_key> poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或者使用 .env 文件（推荐）：

```bash
cd apps/api
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 打开 Web UI

在浏览器中打开：
```
apps/web/index.html
```

### 3. 使用示例

**完整信息输入：**
```
周五前完成路演PPT，大概3小时
```

**需要澄清的输入：**
```
做个方案
```
AI 会询问截止时间和所需时长（最多2轮）

## 功能特性

- ✅ 中文自然语言解析（日期、时长）
- ✅ 智能澄清流程（最多2轮，自动兜底）
- ✅ 自动优先级判断（基于截止时间）
- ✅ 排程算法（避开忙碌时段，拆分任务块）
- ✅ Google Calendar 集成准备
- ✅ 简单 Web 界面

## API 端点

- `POST /api/parse` - 解析任务文本
- `POST /api/intake` - 任务接入（含澄清）
- `POST /api/schedule` - 生成日程
- `GET /health` - 健康检查

## 测试

```bash
cd apps/api
DEEPSEEK_API_KEY=<your_key> poetry run pytest tests/ -v
```

当前：51 个测试全部通过

## 技术栈

- **Backend**: FastAPI + Python 3.11+
- **LLM**: Claude Sonnet 4.6 (via skyapi.org)
- **Frontend**: 原生 HTML/JS
- **Database**: SQLAlchemy (未启用)

## 故障排除

### API Key 错误
如果遇到 "DEEPSEEK_API_KEY not set" 错误：
1. 确认 `.env` 文件存在且包含正确的 API key
2. 或者在启动命令中显式设置环境变量

### 端口被占用
如果 8000 端口被占用：
```bash
# 查找占用端口的进程
lsof -i :8000
# 杀掉进程
kill <PID>
```

### 测试失败
确保使用正确的 API key 运行测试：
```bash
DEEPSEEK_API_KEY=<your_key> poetry run pytest tests/ -v
```
