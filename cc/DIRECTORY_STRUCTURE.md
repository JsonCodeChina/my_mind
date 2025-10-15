# ccnews 目录结构说明

> 优化后的清晰目录结构（v2.1）

---

## 📁 目录树

```
cc/
├── 📋 README.md                    # 主文档 - 从这里开始
├── ⚙️ config.json                  # 配置文件 - 所有设置
├── 📊 baseline.json                # 基线数据 - 版本追踪
├── 🔗 urls.txt                     # URL 列表（已集成到 config）
│
├── 📁 docs/                        # 📚 文档目录
│   ├── CHANGELOG.md                # 版本历史
│   ├── QUICK_REFERENCE.md          # 快速参考
│   ├── INCREMENTAL_UPDATE_GUIDE.md # 增量更新指南
│   ├── OUTPUT_OPTIMIZATION.md      # 输出优化说明
│   └── V2.1_UPGRADE_SUMMARY.md     # v2.1 升级总结
│
├── 📁 cache/                       # 💾 缓存数据
│   ├── articles.json               # 文章缓存（追踪新文章）
│   ├── versions.json               # 版本缓存（检测版本变化）
│   └── community.json              # 社区缓存（Issue、讨论）
│
├── 📁 templates/                   # 📄 模板文件
│   ├── minimal-index.html          # 极简 HTML 模板
│   ├── minimal-daily.md            # 极简 Markdown 模板
│   ├── daily-incremental.md        # 增量更新模板
│   ├── quick-changes.md            # 快速变化模板
│   └── index-template.html         # 完整 HTML 模板
│
├── 📁 styles/                      # 🎨 样式文件
│   └── minimal.css                 # 极简样式（3KB，所有页面共享）
│
├── 📁 scripts/                     # 🤖 自动化脚本
│   └── daily-ccnews.sh             # 每日自动生成脚本
│
├── 📁 archive/                     # 🗄️ 历史报告归档
│   └── 2025-10/                    # 按月归档
│       ├── 2025-10-13/             # 每日报告
│       ├── 2025-10-13-update/
│       └── 2025-10-13-v2/
│
└── 📁 logs/                        # 📝 日志文件
    └── ccnews-auto-*.log           # 自动化日志
```

---

## 📋 目录说明

### 根目录文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `README.md` | 主文档，系统介绍和使用指南 | 11KB |
| `config.json` | 配置文件，所有设置集中管理 | 2.6KB |
| `baseline.json` | 基线数据，记录版本和运行历史 | 746B |
| `urls.txt` | URL 列表（已集成到 config.json） | 157B |

### docs/ - 文档目录

所有详细文档集中存放，保持根目录简洁。

| 文件 | 说明 | 大小 |
|------|------|------|
| `CHANGELOG.md` | 版本更新历史 | 7KB |
| `QUICK_REFERENCE.md` | 快速参考手册 | 5KB |
| `INCREMENTAL_UPDATE_GUIDE.md` | 增量更新详细指南 | 8KB |
| `OUTPUT_OPTIMIZATION.md` | 输出优化说明（90% token 节约） | 9KB |
| `V2.1_UPGRADE_SUMMARY.md` | v2.1 升级总结 | 8KB |

### cache/ - 缓存数据

持久化数据，用于增量更新和变化检测。

| 文件 | 说明 | 更新频率 |
|------|------|---------|
| `articles.json` | 文章缓存（URL、标题、首次发现时间） | 每次运行 |
| `versions.json` | 版本缓存（版本号、发布日期） | 每次运行 |
| `community.json` | 社区缓存（Issue、HN、Reddit） | 每次运行 |

### templates/ - 模板文件

所有输出模板，支持自定义。

| 文件 | 说明 | 用途 |
|------|------|------|
| `minimal-index.html` | 极简 HTML 模板 | 默认输出（推荐） |
| `minimal-daily.md` | 极简 Markdown 模板 | 默认输出（推荐） |
| `daily-incremental.md` | 增量更新模板 | 仅显示变化 |
| `quick-changes.md` | 快速变化模板 | 3 分钟浏览版 |
| `index-template.html` | 完整 HTML 模板 | 首次运行 |

### styles/ - 样式文件

外部 CSS，所有 HTML 共享。

| 文件 | 说明 | 大小 |
|------|------|------|
| `minimal.css` | 极简样式（支持深色模式） | 3KB |

### scripts/ - 自动化脚本

定时任务和自动化脚本。

| 文件 | 说明 | 用途 |
|------|------|------|
| `daily-ccnews.sh` | 每日自动生成脚本 | cron 定时任务 |

### archive/ - 历史归档

所有历史报告按月归档，保持根目录整洁。

```
archive/
├── 2025-10/
│   ├── 2025-10-13/          # 每日报告
│   │   ├── index.html
│   │   └── DAILY.md
│   ├── 2025-10-14/
│   └── ...
├── 2025-11/
└── ...
```

### logs/ - 日志文件

自动化脚本的运行日志。

```
logs/
├── ccnews-auto-2025-10-13.log
├── ccnews-auto-2025-10-14.log
└── ...
```

---

## 🚀 使用方式

### 查看今日报告

```bash
# 最新报告在 archive 目录下
open archive/2025-10/$(date +%Y-%m-%d)/index.html

# 或查看 Markdown 版本
cat archive/2025-10/$(date +%Y-%m-%d)/DAILY.md
```

### 运行 ccnews

```bash
# 在 Claude Code 中执行
/ccnews

# 或手动运行脚本
./scripts/daily-ccnews.sh
```

### 查看文档

```bash
# 主文档
cat README.md

# 快速参考
cat docs/QUICK_REFERENCE.md

# 增量更新指南
cat docs/INCREMENTAL_UPDATE_GUIDE.md
```

---

## 📊 目录优化效果

### 优化前（v2.0）

```
cc/
├── 大量根目录文件（15+ 个） ❌
├── 多个日期目录（2025-10-13, 2025-10-13-update, ...） ❌
└── 文档分散（README.md, CHANGELOG.md, ...） ❌
```

**问题**：
- 根目录太乱，难以找到核心文件
- 历史报告占据根目录空间
- 文档分散，不便管理

### 优化后（v2.1）

```
cc/
├── 4 个核心文件（README, config, baseline, urls） ✅
├── 6 个功能目录（清晰分类） ✅
└── 历史报告归档（按月整理） ✅
```

**优势**：
- ✅ 根目录简洁（仅 4 个核心文件）
- ✅ 文档集中（docs/ 目录）
- ✅ 历史归档（archive/ 按月整理）
- ✅ 功能分离（templates, styles, scripts, cache）
- ✅ 易于维护（清晰的结构）

---

## 💡 维护建议

### 每日维护

- 历史报告自动归档到 `archive/YYYY-MM/`
- 日志自动清理（保留 30 天）

### 每月维护

- 检查 `archive/` 大小，可选择压缩旧月份
- 清理 `cache/` 中的过期数据

### 配置更新

所有配置集中在 `config.json`，修改后立即生效。

---

## 🔗 快速导航

| 需求 | 文件位置 |
|------|---------|
| 📖 开始使用 | `README.md` |
| ⚙️ 修改配置 | `config.json` |
| 📚 查看文档 | `docs/` |
| 📊 查看今日报告 | `archive/YYYY-MM/YYYY-MM-DD/` |
| 🎨 自定义样式 | `styles/minimal.css` |
| 📄 自定义模板 | `templates/` |
| 🤖 自动化脚本 | `scripts/daily-ccnews.sh` |

---

📅 最后更新：2025-10-13
🎯 优化版本：v2.1
✨ 目录结构：简洁、清晰、易维护
