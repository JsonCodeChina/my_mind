#!/bin/bash
# Quick Report Generator
# 一键生成 Claude Code 日报

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Claude Code 快速报告生成"
echo "=========================================="
echo ""

# 进入工作目录
cd "$CC_DIR"

# 1. 激活虚拟环境并采集数据
echo "📥 步骤 1/3: 采集数据..."
source .meta/venv/bin/activate
python .meta/scripts/fetch_data_v2.py

if [ $? -ne 0 ]; then
    echo "❌ 数据采集失败"
    exit 1
fi

echo "✅ 数据采集完成"
echo ""

# 2. 提示用户运行 AI 分析
echo "🤖 步骤 2/3: AI 分析"
echo ""
echo "请在 Claude Code 中运行以下命令生成报告:"
echo ""
echo "  /ccnews"
echo ""
echo "或者手动分析数据:"
echo "  数据文件: .meta/cache/daily_data.json"
echo "  Agent规范: .claude/agents/ccnews-analyst.md"
echo ""

# 3. 显示最新报告位置
LATEST_REPORT=$(ls -t 2025-*/index.md 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo "📊 最新报告: $LATEST_REPORT"
    echo "   行数: $(wc -l < "$LATEST_REPORT")"
    echo "   大小: $(du -h "$LATEST_REPORT" | cut -f1)"
fi

echo ""
echo "=========================================="
echo "提示："
echo "  - 查看报告: cat $LATEST_REPORT"
echo "  - 查看数据库: sqlite3 ainews.db"
echo "  - 清理旧数据: .meta/scripts/db-cleanup.sh"
echo "=========================================="
