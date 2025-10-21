#!/bin/bash
# 数据库备份脚本

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/.shared/backups"
DATE=$(date +"%Y-%m-%d")

mkdir -p "$BACKUP_DIR"

# 备份 ccnews 数据库
if [ -f "$PROJECT_ROOT/cc/ccnews.db" ]; then
    echo "备份 ccnews.db..."
    sqlite3 "$PROJECT_ROOT/cc/ccnews.db" ".backup $BACKUP_DIR/ccnews_${DATE}.db"
    echo "✓ 备份完成: $BACKUP_DIR/ccnews_${DATE}.db"
fi

# 压缩旧备份（保留最近 7 天）
find "$BACKUP_DIR" -name "*.db" -mtime +7 -exec gzip {} \;

# 删除超过 30 天的压缩备份
find "$BACKUP_DIR" -name "*.db.gz" -mtime +30 -delete

echo "✓ 备份任务完成"
ls -lh "$BACKUP_DIR"
