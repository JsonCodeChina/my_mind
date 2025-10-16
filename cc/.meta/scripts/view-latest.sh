#!/bin/bash
# View Latest Report
# 快速查看最新报告

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$CC_DIR"

# 查找最新报告
LATEST_REPORT=$(ls -t 2025-*/index.md 2>/dev/null | head -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ 未找到任何报告"
    echo ""
    echo "提示: 运行 .meta/scripts/quick-report.sh 生成报告"
    exit 1
fi

echo "=========================================="
echo "最新报告: $LATEST_REPORT"
echo "=========================================="
echo ""
echo "📊 统计:"
echo "  行数: $(wc -l < "$LATEST_REPORT")"
echo "  字数: $(wc -w < "$LATEST_REPORT")"
echo "  大小: $(du -h "$LATEST_REPORT" | cut -f1)"
echo "  更新: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_REPORT" 2>/dev/null || stat -c "%y" "$LATEST_REPORT" 2>/dev/null | cut -d'.' -f1)"
echo ""
echo "=========================================="
echo ""

# 显示报告内容
cat "$LATEST_REPORT"

echo ""
echo "=========================================="
echo "快捷命令:"
echo "  在浏览器打开: open $LATEST_REPORT"
echo "  在VSCode打开: code $LATEST_REPORT"
echo "  复制到剪贴板: cat $LATEST_REPORT | pbcopy"
echo "=========================================="
