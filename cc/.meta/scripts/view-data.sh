#!/bin/bash
# View Cached Data
# 查看缓存的数据

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATA_FILE="$CC_DIR/.meta/cache/daily_data.json"

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ 数据文件不存在: $DATA_FILE"
    echo ""
    echo "提示: 运行 .meta/scripts/quick-report.sh 采集数据"
    exit 1
fi

echo "=========================================="
echo "缓存数据: $DATA_FILE"
echo "=========================================="
echo ""
echo "📊 文件信息:"
echo "  大小: $(du -h "$DATA_FILE" | cut -f1)"
echo "  更新: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$DATA_FILE" 2>/dev/null || stat -c "%y" "$DATA_FILE" 2>/dev/null | cut -d'.' -f1)"
echo ""

# 使用 jq 显示摘要（如果安装了jq）
if command -v jq &> /dev/null; then
    echo "📈 数据摘要:"
    jq -r '
    "  版本: " + .version.current,
    "  Issues: " + (.issues | length | tostring),
    "  HN讨论: " + (.discussions | length | tostring),
    "  采集时间: " + .metadata.timestamp
    ' "$DATA_FILE"

    echo ""
    echo "🔥 热门Issues:"
    jq -r '
    .issues[] |
    "  #" + (.number | tostring) + " - " + .title + " (热度: " + (.heat_score | tostring) + ")"
    ' "$DATA_FILE" | head -5
else
    echo "💡 安装 jq 可查看更详细的数据摘要:"
    echo "   brew install jq"
    echo ""
    echo "📄 原始数据:"
    head -50 "$DATA_FILE"
fi

echo ""
echo "=========================================="
echo "查看完整数据:"
echo "  cat $DATA_FILE | jq ."
echo "  code $DATA_FILE"
echo "=========================================="
