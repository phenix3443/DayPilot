#!/bin/bash
# 激活 poetry 虚拟环境并设置 prompt_collector 环境变量

export PROMPT_COLLECTOR_API_URL="https://prompt-cacher.bitkinetic.com/"
export PROMPT_COLLECTOR_USERNAME="liushangliang_hackson"

# 激活 poetry shell
poetry shell
