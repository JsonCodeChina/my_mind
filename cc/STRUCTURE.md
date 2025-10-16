# Claude Code News 目录结构（重组版）

```
cc/
├── 📅 每日报告（主要关注）
│   ├── 2025-10-14/
│   │   └── index.md
│   ├── 2025-10-15/
│   │   └── index.md
│   └── 2025-10-16/
│       └── index.md                      # ✅ 最新报告（161行深度版）
│
├── 📦 归档区
│   └── archive/
│       └── 2025-10/                      # 历史报告归档
│
├── 🗄️ 数据库
│   └── ainews.db                         # ✅ SQLite（历史数据持久化）
│
├── 🔧 辅助系统（.meta/）
│   ├── 🤖 scripts/                       # 数据采集脚本
│   │   ├── fetch_data_v2.py              # ✅ 核心采集脚本
│   │   ├── db_manager.py                 # 数据库管理
│   │   ├── daily-ccnews.sh               # 快速执行
│   │   └── view-latest.sh                # 查看最新报告
│   │
│   ├── 💾 cache/                         # 数据缓存
│   │   └── daily_data.json               # ✅ 每日数据（16KB）
│   │
│   ├── 📋 templates/                     # 报告模板
│   │   ├── minimal-daily.md              # 精简模板
│   │   └── ...
│   │
│   ├── 📐 schemas/                       # 数据结构定义
│   │   ├── daily_data.schema.json
│   │   └── daily_data.example.json
│   │
│   ├── 📚 docs/                          # 文档
│   │   ├── CHANGELOG.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── ...
│   │
│   ├── 🎨 styles/                        # CSS样式
│   │   └── minimal.css
│   │
│   ├── 🔬 research/                      # 研究资料
│   │   └── api-feasibility.md
│   │
│   ├── 🐍 venv/                          # Python虚拟环境
│   │
│   └── 📦 配置文件
│       ├── baseline.json                 # 版本基线
│       ├── config.json                   # 配置参数
│       ├── requirements.txt              # Python依赖
│       └── urls.txt                      # 优质资源链接
│
└── 📝 项目文档（根目录）
    ├── README.md                         # 项目总览
    ├── STRUCTURE.md                      # ✅ 本文件（目录结构）
    ├── DIRECTORY_STRUCTURE.md            # 旧版结构说明
    └── OPTIMIZATION_SUMMARY.md           # 优化总结

```

## 核心改进

### 重组目标
✅ **突出每日报告**：根目录直接展示 2025-10-xx/ 文件夹
✅ **集中辅助文件**：所有脚本、配置、模板统一放在 `.meta/`
✅ **清爽根目录**：只保留报告、归档、数据库和文档

### 对比优化前

**优化前**（16个顶级项目）:
```
cc/
├── 2025-10-14/
├── 2025-10-15/
├── 2025-10-16/
├── archive/
├── baseline.json      ← 分散
├── cache/             ← 分散
├── config.json        ← 分散
├── docs/              ← 分散
├── requirements.txt   ← 分散
├── schemas/           ← 分散
├── scripts/           ← 分散
├── styles/            ← 分散
├── templates/         ← 分散
├── urls.txt           ← 分散
├── venv/              ← 分散
└── README.md
```

**优化后**（5个顶级项目）:
```
cc/
├── 2025-10-14/        ← 每日报告
├── 2025-10-15/        ← 每日报告
├── 2025-10-16/        ← 每日报告
├── archive/           ← 归档
├── ainews.db          ← 数据库
├── .meta/             ← 所有辅助文件
└── README.md          ← 文档
```

## 工作流程（保持不变）

### 1. 数据采集（~20秒）
```bash
cd /Users/shenbo/Desktop/mind/cc
source .meta/venv/bin/activate
python .meta/scripts/fetch_data_v2.py
```

输出：
- `.meta/cache/daily_data.json`（16KB）
- `ainews.db`（114KB，自动更新）

### 2. AI 分析（~15秒）
通过 `.claude/agents/ccnews-analyst.md` 规范：
```
读取：.meta/cache/daily_data.json
输出：2025-10-16/index.md（161行）
```

### 3. 数据流
```
GitHub API → fetch_data_v2.py → .meta/cache/daily_data.json → AI → index.md
                ↓
           ainews.db (持久化)
```

## 路径更新说明

### 脚本中的路径已更新
- `fetch_data_v2.py`:
  - 输出路径：`/Users/shenbo/Desktop/mind/cc/.meta/cache/daily_data.json`
- `db_manager.py`:
  - 数据库路径：`/Users/shenbo/Desktop/mind/cc/ainews.db`

### Agent 配置需要更新
- `.claude/agents/ccnews-analyst.md` 中读取数据路径需改为：
  - `cc/.meta/cache/daily_data.json`

## 测试结果

✅ 虚拟环境重建成功
✅ 依赖安装正常（requests, beautifulsoup4, python-dateutil）
✅ 脚本可正常调用（--help 测试通过）
✅ 路径引用已更新

## 优势总结

1. **清爽可见**：根目录只有每日报告和归档，一目了然
2. **集中管理**：所有辅助文件在 `.meta/` 下统一管理
3. **易于导航**：用户直接关注日报文件夹
4. **维护简单**：脚本、配置、模板集中在一处
5. **扩展友好**：新增辅助文件放入 `.meta/` 即可

## 使用建议

- **日常查看**：直接打开 `2025-10-xx/index.md`
- **生成报告**：运行 `/ccnews` 命令
- **查看配置**：进入 `.meta/` 查看脚本和配置
- **归档管理**：旧报告自动移入 `archive/`
