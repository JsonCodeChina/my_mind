#!/bin/bash
# Database Cleanup Script
# 清理数据库中的旧数据

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DB_FILE="$CC_DIR/ainews.db"

# 默认保留30天
DAYS=${1:-30}

echo "=========================================="
echo "数据库清理工具"
echo "=========================================="
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ 数据库文件不存在: $DB_FILE"
    exit 1
fi

echo "📊 清理前统计:"
sqlite3 "$DB_FILE" <<EOF
SELECT
    '  Issues: ' || COUNT(*)
FROM issues;
SELECT
    '  Comments: ' || COUNT(*)
FROM issue_comments;
SELECT
    '  HN Discussions: ' || COUNT(*)
FROM hn_discussions;
EOF

echo ""
echo "🗑️  删除 $DAYS 天前的数据..."

# 计算截止日期
CUTOFF_DATE=$(date -u -v-${DAYS}d +"%Y-%m-%d %H:%M:%S" 2>/dev/null || date -u -d "$DAYS days ago" +"%Y-%m-%d %H:%M:%S")

sqlite3 "$DB_FILE" <<EOF
DELETE FROM issues WHERE fetched_at < '$CUTOFF_DATE';
DELETE FROM issue_comments WHERE fetched_at < '$CUTOFF_DATE';
DELETE FROM hn_discussions WHERE fetched_at < '$CUTOFF_DATE';
DELETE FROM hn_comments WHERE fetched_at < '$CUTOFF_DATE';
VACUUM;
EOF

echo "✅ 清理完成"
echo ""
echo "📊 清理后统计:"
sqlite3 "$DB_FILE" <<EOF
SELECT
    '  Issues: ' || COUNT(*)
FROM issues;
SELECT
    '  Comments: ' || COUNT(*)
FROM issue_comments;
SELECT
    '  HN Discussions: ' || COUNT(*)
FROM hn_discussions;
EOF

echo ""
echo "💾 数据库大小: $(du -h "$DB_FILE" | cut -f1)"
echo ""
echo "=========================================="
echo "用法: $0 [天数]"
echo "示例: $0 60  # 清理60天前的数据"
echo "=========================================="
