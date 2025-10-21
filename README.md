# Mind - AI 技术追踪与动态分析

这是一个综合性的 AI 技术追踪项目，包含多个子模块，用于监控和分析 AI 行业的最新动态。

## 项目结构

```
mind/
├── cc/                      # Claude Code 专项追踪
│   ├── .meta/              # 元数据、脚本、数据库
│   ├── YYYY-MM-DD/         # 每日 Claude Code 动态报告
│   ├── archive/            # 历史报告归档
│   └── README.md           # Claude Code 模块说明
│
├── ainews/                  # AI 行业全景动态
│   ├── .meta/              # 元数据和采集脚本
│   ├── YYYY-MM-DD/         # 每日 AI 全景报告
│   ├── archive/            # 历史报告归档
│   └── README.md           # AI News 模块说明
│
└── .claude/                # Claude Code 配置
    ├── commands/           # 自定义命令
    │   ├── ccnews.md      # /ccnews 命令
    │   └── ainews.md      # /ainews 命令
    └── agents/             # 专用 Agent
        └── ainews-analyst.md
```

## 功能模块

### 1. Claude Code 追踪 (`/ccnews`)

专注于 Claude Code 的开发动态：
- GitHub Issues 热度追踪
- 社区讨论分析
- 版本更新监控
- 用户反馈趋势

**生成报告**：`/ccnews`
**输出路径**：`cc/YYYY-MM-DD/index.md`

### 2. AI 全景动态 (`/ainews`)

涵盖整个 AI 行业的动态：
- 模型排行榜（LMSYS）
- 行业新闻（Anthropic、OpenAI 等）
- 社区热议（Reddit、HN）
- 开发工具动态

**生成报告**：`/ainews`
**输出路径**：`ainews/YYYY-MM-DD/index.md`

## 快速开始

### 生成今日报告

```bash
# Claude Code 专项报告
/ccnews

# AI 全景动态报告
/ainews
```

### 查看历史报告

```bash
# Claude Code 报告
cd cc/2025-10-17
cat index.md

# AI 全景报告
cd ainews/2025-10-17
cat index.md
```

## 技术栈

- **数据采集**: WebFetch, Web Search, GitHub API, Python 脚本
- **数据存储**: SQLite (cc/ccnews.db)
- **报告生成**: Claude Sonnet 4.5
- **自动化**: Claude Code 自定义命令

## 维护

- 报告每日自动生成
- 数据库每日更新
- 历史报告按月归档

---

*Powered by Claude Code*
