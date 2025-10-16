# Scripts 使用指南

这里包含所有辅助脚本，用于数据采集、报告生成和系统维护。

## 🚀 快速开始

### 一键生成报告
```bash
./quick-report.sh
```
自动执行数据采集，提示你运行 AI 分析。

---

## 📜 脚本列表

### 数据采集

**fetch_data_v2.py** - 核心数据采集脚本
```bash
# 基本使用
python fetch_data_v2.py

# 自定义参数
python fetch_data_v2.py --github-days 7 --hn-days 14 --verbose

# 指定输出路径
python fetch_data_v2.py -o /path/to/output.json
```

采集内容：
- GitHub Issues（最近3天，热度>30）
- 高质量评论（10-20条/issue）
- HN 讨论（最近7天，热度>70）
- 版本信息

输出：
- `.meta/cache/daily_data.json`
- `ainews.db`（SQLite数据库）

---

### 数据库管理

**db-stats.sh** - 查看数据库统计
```bash
./db-stats.sh
```

显示：
- 总体统计（Issues、评论、讨论数）
- Top 10 热门 Issues
- 最新数据时间
- 数据库大小

**db-cleanup.sh** - 清理旧数据
```bash
# 清理30天前的数据（默认）
./db-cleanup.sh

# 清理60天前的数据
./db-cleanup.sh 60
```

清理：
- Issues
- 评论
- HN 讨论
- 执行 VACUUM 优化数据库

**db_manager.py** - Python数据库管理模块
```python
from db_manager import DatabaseManager

db = DatabaseManager()
db.insert_issue(issue_data)
db.get_issue_trend(issue_number, days=7)
db.cleanup_old_data(days=30)
```

---

### 报告查看

**view-latest.sh** - 查看最新报告
```bash
./view-latest.sh
```

显示：
- 报告统计（行数、字数、大小）
- 完整报告内容
- 快捷命令提示

**view-data.sh** - 查看缓存数据
```bash
./view-data.sh
```

显示：
- 缓存文件信息
- 数据摘要（需要 jq）
- 热门 Issues 列表

---

### 快捷脚本

**quick-report.sh** - 快速生成报告
```bash
./quick-report.sh
```

流程：
1. 激活虚拟环境
2. 运行数据采集
3. 提示运行 AI 分析
4. 显示最新报告信息

---

### 自动化（已废弃）

**daily-ccnews.sh** - 自动化脚本（v2.1旧版）

⚠️ 此脚本为旧版本，不适用于当前 v3.0 架构。
建议使用 `quick-report.sh` 代替。

---

## 🔧 开发工具

### 数据库操作
```bash
# 连接数据库
sqlite3 ../../ainews.db

# 查询示例
sqlite> SELECT COUNT(*) FROM issues;
sqlite> SELECT * FROM issues WHERE issue_number=8763;
sqlite> SELECT * FROM issues ORDER BY heat_score DESC LIMIT 10;
```

### Python环境
```bash
# 激活虚拟环境
source ../venv/bin/activate

# 安装依赖
pip install -r ../requirements.txt

# 测试数据库
python -c "from db_manager import DatabaseManager; db = DatabaseManager(); print('✅ OK')"
```

---

## 📊 工作流程

### 完整流程
```bash
# 1. 采集数据
./quick-report.sh

# 2. 在 Claude Code 中运行
/ccnews

# 3. 查看报告
./view-latest.sh

# 4. 查看数据库统计
./db-stats.sh
```

### 维护流程
```bash
# 每周清理
./db-cleanup.sh 30

# 检查数据
./db-stats.sh
./view-data.sh
```

---

## ⚡ 性能优化

### 数据采集优化
- 默认3天GitHub Issues（可调整为7天）
- 默认7天HN讨论（可调整为14天）
- 自动重试失败请求（3次）
- 并发评论抓取

### 数据库优化
- 定期 VACUUM（db-cleanup.sh 自动执行）
- 索引优化（自动创建）
- 定期清理旧数据（建议30天）

---

## 🐛 故障排除

### 数据采集失败
**问题**: GitHub API rate limit
```bash
# 检查限制
curl -s https://api.github.com/rate_limit

# 等待1小时或设置 GitHub token
```

### Python环境问题
**问题**: ModuleNotFoundError
```bash
# 重建虚拟环境
rm -rf ../venv
python3 -m venv ../venv
source ../venv/bin/activate
pip install -r ../requirements.txt
```

### 数据库锁定
**问题**: database is locked
```bash
# 关闭所有 sqlite3 连接
# 删除锁文件
rm ../../ainews.db-journal
rm ../../ainews.db-shm
rm ../../ainews.db-wal
```

---

## 📝 脚本参数

### fetch_data_v2.py
```
--output, -o          输出文件路径
--github-days         GitHub Issues 回溯天数（默认3）
--hn-days             HN 讨论回溯天数（默认7）
--verbose, -v         显示详细日志
```

### db-cleanup.sh
```
参数1: 保留天数（默认30）
```

---

## 🔗 相关文档

- [README.md](../../README.md) - 项目总览
- [STRUCTURE.md](../../STRUCTURE.md) - 目录结构
- [ccnews-analyst.md](../../../.claude/agents/ccnews-analyst.md) - AI分析规范

---

📅 最后更新：2025-10-16
🤖 Claude Code News System v3.0
