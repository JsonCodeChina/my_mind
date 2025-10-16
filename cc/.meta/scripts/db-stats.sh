#!/bin/bash
# Database Statistics Viewer
# 查看数据库统计信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DB_FILE="$CC_DIR/ainews.db"

echo "=========================================="
echo "数据库统计信息"
echo "=========================================="
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ 数据库文件不存在: $DB_FILE"
    exit 1
fi

echo "📊 总体统计:"
sqlite3 "$DB_FILE" <<EOF
.mode column
.headers on
.width 30 15

SELECT
    'Total Issues' as Metric,
    COUNT(*) as Count
FROM issues
UNION ALL
SELECT
    'Total Comments',
    COUNT(*)
FROM issue_comments
UNION ALL
SELECT
    'Total HN Discussions',
    COUNT(*)
FROM hn_discussions
UNION ALL
SELECT
    'Total HN Comments',
    COUNT(*)
FROM hn_comments;
EOF

echo ""
echo "🔥 Top 10 热门 Issues:"
sqlite3 "$DB_FILE" <<EOF
.mode column
.headers on
.width 8 10 50 12

SELECT
    issue_number as 'Issue',
    ROUND(heat_score, 1) as 'Heat',
    substr(title, 1, 45) || '...' as 'Title',
    substr(updated_at, 1, 10) as 'Updated'
FROM issues
ORDER BY heat_score DESC
LIMIT 10;
EOF

echo ""
echo "📅 最新数据:"
sqlite3 "$DB_FILE" <<EOF
.mode column
.headers on

SELECT
    '  Latest fetch: ' || MAX(fetched_at)
FROM issues;
EOF

echo ""
echo "💾 数据库信息:"
echo "  文件大小: $(du -h "$DB_FILE" | cut -f1)"
echo "  位置: $DB_FILE"
echo ""
echo "=========================================="
echo "详细查询:"
echo "  sqlite3 $DB_FILE"
echo "  > SELECT * FROM issues WHERE issue_number=8763;"
echo "=========================================="
