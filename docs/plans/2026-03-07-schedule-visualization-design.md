# 日程可视化设计文档

## 1. 需求概述

为 DayPilot Web UI 添加日程可视化功能，支持多种展示方式和丰富的交互功能。

### 用户需求
- 支持三种视图：时间轴视图、列表视图、卡片视图
- 提供视图切换功能
- 支持交互：拖拽调整时间、点击查看详情、删除时间块、编辑字段

### 当前状态
- Web UI: 简单的 HTML/JS，已实现任务输入和基础日程展示
- API: `/api/schedule` 返回时间块数组
- 时间块格式: `{title, start, end, duration_minutes}`

## 2. 架构设计

### 2.1 组件结构

```
ScheduleView (容器)
├── ViewSwitcher (视图切换器)
├── TimelineView (时间轴视图)
├── ListView (列表视图)
└── CardView (卡片视图)
```

### 2.2 数据流

```
用户输入 → API /api/intake → API /api/schedule → 时间块数据 → 可视化组件
```

## 3. 技术方案

### 3.1 视图实现

**时间轴视图**
- 使用 CSS Grid 布局
- 横轴：时间（小时刻度）
- 纵轴：日期
- 时间块：绝对定位，根据开始/结束时间计算位置

**列表视图**
- 简单的 `<ul>` 列表
- 每项显示：标题、时间范围、时长

**卡片视图**
- Flexbox 布局
- 每个时间块一张卡片
- 显示完整信息

### 3.2 交互功能

**拖拽调整**
- 使用 HTML5 Drag and Drop API
- 拖拽时计算新的开始时间
- 调用 API 更新（需要新增 PATCH 端点）

**点击查看详情**
- Modal 弹窗显示详细信息
- 包含编辑表单

**删除时间块**
- 确认对话框
- 调用 API 删除（需要新增 DELETE 端点）

**编辑字段**
- 内联编辑或弹窗编辑
- 支持修改：标题、开始时间、结束时间

## 4. API 需求

需要新增以下端点：

- `PATCH /api/schedule/{block_id}` - 更新时间块
- `DELETE /api/schedule/{block_id}` - 删除时间块
- `GET /api/schedule` - 获取当前日程（可选）

## 5. 实现优先级

**Phase 1: 基础可视化**
1. 三种视图的静态展示
2. 视图切换功能

**Phase 2: 基础交互**
3. 点击查看详情
4. 删除时间块

**Phase 3: 高级交互**
5. 拖拽调整时间
6. 编辑字段

## 6. 技术栈

- 纯 HTML/CSS/JS（保持简单）
- 不引入额外框架
- 使用现代 CSS（Grid, Flexbox）
- 使用原生 Drag and Drop API
