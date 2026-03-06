# DayPilot Project - Prompt Collector Setup

## 配置说明

本项目已配置 prompt_collector 用于记录 AI 对话过程。

### 环境变量
- API URL: `https://prompt-cacher.bitkinetic.com/`
- 用户名: `liushangliang_hackson`

### 使用方法

直接在项目目录中启动 Claude Code：
```bash
cd /path/to/DayPilot
claude
```

环境变量会从 `.env` 文件自动加载。

如果需要在命令行中使用 prompt_collector，先加载环境变量：
```bash
source .env
poetry run prompt-collector --type prompt --session-id "test" --content "hello"
```

### 手动使用

```bash
# 发送 prompt
echo '{"session_id": "your_session", "content": "your prompt"}' | poetry run prompt-collector --type prompt

# 发送 result
echo '{"session_id": "your_session", "content": "AI response"}' | poetry run prompt-collector --type result
```

### 注意事项

- prompt_collector 仅在当前项目的 poetry 虚拟环境中生效
- 不会影响其他项目或全局环境
- 环境变量配置在 `.envrc` 文件中（需要 direnv）或通过 `activate_prompt_collector.sh` 脚本设置
