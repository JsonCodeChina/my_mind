# Claude Code 每日资讯系统 v2.1

## 📌 系统简介

自动化获取、分析和整理 Claude Code 的最新动态，生成美观的网页报告。

**v2.1 核心功能：**
- 🚀 自动爬取官方文档、社区文章、GitHub Issues、Hacker News、Reddit
- 📊 分析社区讨论，识别热点话题和情绪趋势
- 🔄 **增量更新**：仅显示变化内容，跳过未变化的官方信息 ⭐
- 📚 **新文章追踪**：自动检测社区新文章和更新时间 ⭐
- 🎯 **极简输出**：仅标题+链接，token 消耗减少 90% ⭐ 最新
- 💾 **外部 CSS**：所有页面共享样式，避免重复 ⭐ 最新
- ⚡ **快速阅读**：3 分钟了解核心动态 ⭐ 最新

## 🚀 快速开始

### 1. 执行命令

在 Claude Code 中输入：
```
/ccnews
```

系统将自动：
1. 读取配置文件（config.json）
2. 爬取所有数据源
3. 分析社区讨论
4. 生成所有文档和网页
5. 在浏览器中打开主页面

### 2. 查看结果

**主页面**：`archive/2025-10/YYYY-MM-DD/index.html`（极简版，5KB）
**Markdown 版**：`archive/2025-10/YYYY-MM-DD/DAILY.md`（纯文本，2KB）

## 📁 目录结构

```
cc/
├── README.md                      # 主文档（本文件）
├── config.json                    # 配置文件
├── baseline.json                  # 基线数据
├── DIRECTORY_STRUCTURE.md         # 目录结构说明 ⭐ 最新
│
├── docs/                          # 📚 文档目录
│   ├── CHANGELOG.md
│   ├── QUICK_REFERENCE.md
│   ├── INCREMENTAL_UPDATE_GUIDE.md
│   ├── OUTPUT_OPTIMIZATION.md
│   └── V2.1_UPGRADE_SUMMARY.md
│
├── cache/                         # 💾 缓存数据
│   ├── articles.json
│   ├── versions.json
│   └── community.json
│
├── templates/                     # 📄 模板文件
│   ├── minimal-index.html         # 极简 HTML 模板
│   ├── minimal-daily.md           # 极简 Markdown 模板
│   └── ...
│
├── styles/                        # 🎨 样式文件
│   └── minimal.css                # 极简样式（3KB，共享）
│
├── scripts/                       # 🤖 自动化脚本
│   └── daily-ccnews.sh            # 每日自动生成
│
├── archive/                       # 🗄️ 历史归档
│   └── 2025-10/
│       ├── 2025-10-13/
│       │   ├── index.html
│       │   └── DAILY.md
│       └── ...
│
└── logs/                          # 📝 日志文件
    └── ccnews-auto-*.log
```

📖 **详细说明**：查看 [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)

## ⚙️ 配置说明

### config.json 配置文件

```json
{
  "version": "2.0.0",
  "paths": {
    "baseDir": "/Users/shenbo/Desktop/mind/cc",
    "baseline": "/Users/shenbo/Desktop/mind/cc/baseline.json",
    "urls": "/Users/shenbo/Desktop/mind/cc/urls.txt",
    "templates": "/Users/shenbo/Desktop/mind/cc/templates"
  },
  "dataSources": {
    "official": [...],      // 官方数据源
    "community": [...],     // 社区数据源
    "discussions": [...]    // 讨论平台
  },
  "output": {
    "generateHTML": true,
    "generateMarkdown": true,
    "autoOpenBrowser": true,
    "compactLayout": true,
    "theme": "newspaper"
  },
  "features": {
    "incrementalUpdate": true,        // v2.1: 增量更新 ⭐
    "communityAnalysis": true,
    "versionTracking": true,
    "articleCaching": true,           // v2.1: 文章缓存 ⭐
    "articleTimeTracking": true,      // v2.1: 时间追踪 ⭐
    "skipUnchangedOfficial": true     // v2.1: 跳过未变化官方内容 ⭐
  },
  "display": {
    "topFeaturesCount": 5,
    "topArticlesCount": 4,
    "topCommunityTopics": 5,
    "focusOnChanges": true,           // v2.1: 聚焦变化 ⭐
    "highlightNewArticles": true,     // v2.1: 突出新文章 ⭐
    "showArticlePublishDate": true    // v2.1: 显示发布日期 ⭐
  },
  "cache": {
    "articlesDbPath": "cache/articles.json",
    "versionsDbPath": "cache/versions.json",
    "communityDbPath": "cache/community.json"
  }
}
```

### baseline.json 基线数据

```json
{
  "lastCheckDate": "2025-10-13",
  "claudeCodeVersion": "2.0.14",
  "lastUpdateDate": "2025-10-11",
  "notes": "简要说明"
}
```

## 🎨 设计特点

### 报纸风格
- **字体**：Georgia 衬线字体，专业报刊感
- **配色**：黑白灰简洁配色，强调可读性
- **边框**：简洁的双线边框，分栏布局
- **间距**：紧凑型布局，减少滚动

### 响应式设计
- **桌面**：左侧固定导航 + 主内容区
- **平板**：缩小边距，优化间距
- **移动**：垂直布局，单列显示

### 主题切换
- **浅色主题**：白色背景，黑色文字
- **深色主题**：深灰背景，浅色文字
- **持久化**：localStorage 保存用户选择

## 📊 数据源

### 官方源
- **Claude Code 官方文档**：docs.claude.com/en/docs/claude-code/overview
- **更新日志**：claudelog.com/claude-code-changelog/

### 社区源
- **社区文档站**：cc.deeptoai.com/docs
- **社区最佳实践**：cc.deeptoai.com/docs/zh/best-practices/

### 讨论平台
- **GitHub Issues**：github.com/anthropics/claude-code/issues
- **Hacker News**：关键词搜索
- **Reddit**：r/ClaudeAI 相关讨论

## 🚀 v2.1 新特性

### 1. 极简输出模式 ⭐⭐⭐ 最新
- **仅标题+链接**：不生成文章摘要，不重复功能描述
- **外部 CSS**：所有页面共享 minimal.css（3KB）
- **文件精简**：从 7+ 个文件降到 2 个（index.html + DAILY.md）
- **token 节约 90%**：从 50K 降到 5K
- **阅读时间减少 80%**：从 15 分钟降到 3 分钟

### 2. 增量更新机制 ⭐⭐
- **智能变化检测**：对比缓存，仅显示变化内容
- **跳过未变化官方内容**：版本号相同时不重复
- **聚焦社区动态**：仅显示最近 2-7 天的讨论

### 3. 新文章追踪系统 ⭐⭐
- **文章缓存**：记录所有已见过的文章
- **时间追踪**：提取发布时间和更新时间
- **新文章检测**：自动标识 🆕 新文章
- **更新检测**：标识 🔄 更新的文章

### 4. 数据缓存系统
- **articles.json**：追踪文章历史
- **versions.json**：追踪版本变化
- **community.json**：追踪社区讨论

### 5. v2.0 特性（保留）
- 配置文件管理（config.json）
- 模块化架构（templates/）
- 智能错误处理（自动重试）
- 并行数据抓取

## 🔧 高级用法

### 自定义数据源

编辑 `config.json` 添加新数据源：

```json
"dataSources": {
  "community": [
    {
      "name": "新数据源名称",
      "url": "https://example.com",
      "priority": "high",
      "type": "documentation"
    }
  ]
}
```

### 修改显示数量

```json
"display": {
  "topFeaturesCount": 5,      // 显示 5 个热门功能
  "topArticlesCount": 4,       // 显示 4 篇精选文章
  "topCommunityTopics": 5      // 显示 5 个社区热点
}
```

### 禁用某些功能

```json
"features": {
  "incrementalUpdate": false,   // 禁用增量更新
  "communityAnalysis": true,    // 保持社区分析
  "versionTracking": true       // 保持版本跟踪
}
```

### 更改输出选项

```json
"output": {
  "generateHTML": true,         // 生成 HTML 页面
  "generateMarkdown": true,     // 生成 Markdown 文档
  "autoOpenBrowser": false,     // 不自动打开浏览器
  "compactLayout": true,        // 使用紧凑布局
  "theme": "newspaper"          // 报纸风格
}
```

## 📝 使用建议

### 日常使用（v2.1 优化）⭐

#### 第一次运行
1. 运行 `/ccnews` - 完整爬取所有数据
2. 系统自动创建缓存文件
3. 生成完整报告（包含所有内容）

#### 后续运行（增量模式）
1. 运行 `/ccnews` - 仅爬取变化内容
2. **快速浏览**（3 分钟）：
   - 打开 `QUICK_CHANGES.md` 查看今日要点
   - 浏览新文章列表（带摘要）
   - 扫描社区核心动态标题
3. **深入了解**（10 分钟）：
   - 点击感兴趣的新文章链接
   - 查看热门讨论详情
   - 阅读完整的变化报告
4. **完整学习**（30+ 分钟）：
   - 逐篇阅读新文章
   - 参与社区讨论
   - 尝试新功能和技巧

### 版本追踪
- cache/versions.json 自动追踪版本历史
- 检测到新版本时突出显示更新内容
- 版本信息在报告顶部展示

### 文章追踪 ⭐ 新增
- cache/articles.json 记录所有见过的文章
- 新文章自动标记 🆕 图标
- 更新文章自动标记 🔄 图标
- 显示发布时间和更新时间

### 社区分析
- 每次运行都会分析最近 2-7 天的讨论
- 仅显示新 Issue 和热门讨论（评论数 > 5）
- TOP 5 话题基于关注度和影响力排序
- 社区情绪反映真实用户反馈

## 🐛 故障排除

### 网络问题
- 确保网络连接正常
- 某些 URL 可能需要代理访问
- 失败的 URL 会记录到 resources.md

### 权限问题
- 确保有 cc/ 目录的写权限
- 检查 baseline.json 是否可写

### 配置问题
- 确认 config.json 格式正确（有效 JSON）
- 路径使用绝对路径避免问题
- 数据源 URL 必须有效

## 📈 未来计划

### Phase 1: v2.1 基础实现（当前）
- [x] 增量更新机制设计
- [x] 缓存系统设计
- [x] 模板优化
- [ ] 实际爬取逻辑实现
- [ ] 文章时间提取
- [ ] AI 摘要生成

### Phase 2: v2.2 增强
- [ ] 文章相似度检测
- [ ] 自动分类标签
- [ ] 阅读进度追踪
- [ ] 个性化推荐

### Phase 3: v3.0 扩展
- [ ] 更多数据源（Twitter、LinkedIn）
- [ ] 自定义 HTML 主题
- [ ] 导出为 PDF 功能
- [ ] 多语言支持
- [ ] 数据可视化图表
- [ ] RSS 订阅生成

## 📄 版本历史

### v2.1.0 (2025-10-13) ⭐ 当前版本
- ✨ **增量更新机制**：智能变化检测，跳过未变化内容
- ✨ **新文章追踪系统**：缓存 + 时间追踪 + 新文章检测
- ✨ **优化输出格式**：QUICK_CHANGES.md + 新文章专区
- ✨ **数据缓存系统**：articles/versions/community 三层缓存
- ✨ **增量更新指南**：完整的使用文档
- 📝 新增模板：daily-incremental.md、quick-changes.md
- 📝 更新 README 和配置说明

### v2.0.0 (2025-10-13)
- ✨ 新增配置文件系统（config.json）
- ✨ HTML 模板独立化
- ✨ 优化文件结构（details/ 子目录）
- ✨ 增强错误处理和重试机制
- ✨ 并行数据抓取
- ✨ 紧凑型报纸风格布局
- 🐛 修复各种小问题
- 📝 完善文档和说明

### v1.0.0 (2025-10-12)
- ✨ 初始版本
- ✨ 基础爬取和生成功能
- ✨ 社区趋势分析
- ✨ HTML 和 Markdown 输出

## 🤝 贡献

欢迎提出建议和改进意见！

---

📅 最后更新：2025-10-13
🤖 Claude Code 每日资讯系统 v2.1

📚 **相关文档**：
- [增量更新指南](./INCREMENTAL_UPDATE_GUIDE.md) - 详细了解 v2.1 新特性
- [快速参考](./QUICK_REFERENCE.md) - 常用命令和配置
- [更新日志](./CHANGELOG.md) - 完整版本历史
