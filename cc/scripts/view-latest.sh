#!/bin/bash

# 快速查看最新 ccnews 报告
# 用途: ./scripts/view-latest.sh [html|md]

CCNEWS_DIR="/Users/shenbo/Desktop/mind/cc"
ARCHIVE_DIR="$CCNEWS_DIR/archive"

# 查找最新的报告目录
LATEST_REPORT=$(find "$ARCHIVE_DIR" -type d -name "20*-*-*" | sort -r | head -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ 未找到任何报告"
    exit 1
fi

REPORT_DATE=$(basename "$LATEST_REPORT")
INDEX_HTML="$LATEST_REPORT/index.html"
DAILY_MD="$LATEST_REPORT/DAILY.md"

echo "📅 最新报告：$REPORT_DATE"
echo "📁 位置：$LATEST_REPORT"
echo ""

# 根据参数选择查看方式
case "${1:-html}" in
    html)
        if [ -f "$INDEX_HTML" ]; then
            echo "🌐 在浏览器中打开 HTML 版本..."
            open "$INDEX_HTML"
        else
            echo "❌ 未找到 index.html"
            exit 1
        fi
        ;;
    md|markdown)
        if [ -f "$DAILY_MD" ]; then
            echo "📄 显示 Markdown 版本..."
            echo ""
            cat "$DAILY_MD"
        else
            echo "❌ 未找到 DAILY.md"
            exit 1
        fi
        ;;
    *)
        echo "用法: $0 [html|md]"
        echo "  html - 在浏览器中打开 HTML 版本（默认）"
        echo "  md   - 在终端显示 Markdown 版本"
        exit 1
        ;;
esac
