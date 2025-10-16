# Claude Code 每日资讯系统

> 自动化采集、分析 Claude Code 社区动态，生成深度日报

## 🎯 核心特性

- **评论挖掘**: 从50+条评论中筛选最有价值的10-20条
- **趋势分析**: 基于历史数据预测问题修复时间、情绪走向
- **情感洞察**: 不只说"焦虑"，引用评论证明为什么焦虑
- **技术方案**: 识别社区workaround和解决方案
- **数据驱动**: SQLite持久化历史数据，支持趋势对比

## 🚀 快速开始

### 一键生成报告

```bash
/ccnews
```

系统将自动：
1. 采集 GitHub Issues + HN 讨论（~20秒）
2. AI 分析社区评论和趋势（~15秒）
3. 生成 100行左右深度报告（~5秒）

### 查看报告

最新报告：`cc/2025-10-16/index.md`

报告包含：
- 📦 版本动态
- 🔥 热门Issues（含时间线、高赞评论）
- 💬 HN/社区讨论
- 📊 社区脉搏（情绪分析、焦点话题）
- 🎯 编辑精选

## 📁 目录结构

```
cc/
├── 📅 每日报告（主要关注）
│   ├── 2025-10-14/index.md
│   ├── 2025-10-15/index.md
│   └── 2025-10-16/index.md          # 最新报告
│
├── 📦 archive/                      # 历史归档
├── 🗄️ ainews.db                     # SQLite数据库（112KB）
│
├── 🔧 .meta/                        # 辅助系统
│   ├── scripts/                     # 数据采集脚本
│   │   ├── fetch_data_v2.py         # 核心采集脚本
│   │   └── db_manager.py            # 数据库管理
│   ├── cache/                       # 数据缓存
│   │   └── daily_data.json          # 每日数据（22KB）
│   ├── venv/                        # Python环境
│   ├── templates/                   # 报告模板
│   ├── docs/                        # 文档
│   └── baseline.json                # 版本基线
│
└── 📝 文档
    ├── README.md                    # 本文件
    └── STRUCTURE.md                 # 详细目录说明
```

## ⚙️ 工作流程

### 1. 数据采集（~20秒）

```bash
cd /Users/shenbo/Desktop/mind/cc
source .meta/venv/bin/activate
python .meta/scripts/fetch_data_v2.py
```

**采集内容**：
- GitHub Issues（最近3天，热度>30）
- 每个Issue的高质量评论（10-20条）
- HN讨论（最近7天，热度>70）
- 版本信息

**输出**：
- `.meta/cache/daily_data.json`（22KB）
- `ainews.db`（持久化历史数据）

### 2. AI 分析（~15秒）

Agent 自动：
1. 读取 `cc/.meta/cache/daily_data.json`
2. 筛选最有价值的评论（基于quality_score）
3. 分析趋势数据（热度变化、评论增速）
4. 判断社区情绪（引用原文）
5. 生成报告：`cc/2025-10-16/index.md`

**AI规范**：`.claude/agents/ccnews-analyst.md`

### 3. 数据流

```
GitHub API
    ↓
fetch_data_v2.py → daily_data.json → AI分析 → index.md
    ↓
ainews.db (历史数据)
```

## 📊 报告特色

### 时间节点
每个top issue都包含详细时间线：
```markdown
⏱️ 时间线：
- 10-02: Issue创建
- 10-04: 发现根因
- 10-07: 临时方案
- 10-16: 问题持续
```

### 高赞评论
直接引用社区声音：
```markdown
> @semikolon (50👍): "这是灾难性的紧急情况..."
```

### 趋势数据
基于历史对比：
```markdown
热度: 714 ↑ | 评论: 193 (+18/周)
```

### 情感分析
数据支撑的情绪判断：
```markdown
社区情绪：😟 担忧 ↓
证据：50 upvotes评论用词"UNACCEPTABLE"
```

## 🎨 质量标准

- ✅ 100行左右（80-120弹性范围）
- ✅ 5-10条高质量评论
- ✅ 趋势数据完整（↑↓ %）
- ✅ 预测有数据支撑
- ✅ 时间节点清晰

## 🔧 高级用法

### 手动采集数据

```bash
source .meta/venv/bin/activate
python .meta/scripts/fetch_data_v2.py
```

### 查看数据库

```bash
sqlite3 ainews.db
sqlite> SELECT COUNT(*) FROM issues;
sqlite> SELECT * FROM issues ORDER BY heat_score DESC LIMIT 5;
```

### 自定义采集参数

```bash
python .meta/scripts/fetch_data_v2.py \
  --github-days 7 \
  --hn-days 14 \
  --verbose
```

### 数据库清理

```bash
python -c "from .meta.scripts.db_manager import DatabaseManager; \
  db = DatabaseManager(); db.cleanup_old_data(days=30)"
```

## 📚 优质资源

**官方文档**：
- [Claude Code 官方文档](https://docs.claude.com/en/docs/claude-code/overview)
- [Claude Code 最佳实践（中文）](https://cc.deeptoai.com/docs/zh/best-practices/claude-code-best-practices)
- [DeeptoAI 文档中心](https://cc.deeptoai.com/docs)

**实用工具**：
- [更新日志](https://claudelog.com/claude-code-changelog/)
- [插件生态](https://www.anthropic.com/news/claude-code-plugins)

## 🐛 故障排除

### 数据采集失败

**问题**: GitHub API rate limit
**解决**: 等待1小时或设置GitHub token

### 路径错误

**问题**: 脚本找不到文件
**解决**: 确保在 `cc/` 目录下执行

### 虚拟环境问题

**问题**: pip/python not found
**解决**: 重建虚拟环境
```bash
rm -rf .meta/venv
python3 -m venv .meta/venv
source .meta/venv/bin/activate
pip install -r .meta/requirements.txt
```

## 📈 性能指标

- **数据采集**: 15-20秒（含评论抓取）
- **AI分析**: 10-15秒
- **总耗时**: ~30秒
- **Token消耗**: 6-9K
- **评论覆盖**: 10-20条高质量评论
- **数据库大小**: ~112KB（78个issues）

## 🔄 版本历史

### v3.0 (2025-10-16) - 当前版本
- ✨ 目录重组：`.meta/`集中管理辅助文件
- ✨ 评论挖掘：抓取并分析高赞评论
- ✨ 时间节点：为top issues添加详细时间线
- ✨ 优质资源：整合官方文档和工具链接
- ✨ 深度报告：161行（vs 旧版52行）
- 📦 数据持久化：SQLite数据库
- 🎯 情感分析：基于实际评论引用

### v2.1 (2025-10-15)
- 增量更新机制
- 文章追踪系统
- 数据缓存

### v2.0 (2025-10-14)
- 配置文件系统
- HTML模板独立化
- 紧凑型报告

### v1.0 (2025-10-13)
- 初始版本
- 基础爬取和生成

## 🤝 贡献

欢迎提出建议和改进意见！

GitHub: [JsonCodeChina/my_mind](https://github.com/JsonCodeChina/my_mind)

---

📅 最后更新：2025-10-16
🤖 Claude Code 每日资讯系统 v3.0
📖 详细说明：[STRUCTURE.md](./STRUCTURE.md)
