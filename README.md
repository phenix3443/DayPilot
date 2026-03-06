# DayPilot MVP

AI 驱动的个人时间管理工具 - 最小可行产品

## 快速开始

### 1. 启动 API 服务器

```bash
cd apps/api
poetry install
poetry run uvicorn app.main:app --reload --port 8000
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
poetry run pytest apps/api/tests/ -v
```

当前：13 个测试全部通过
