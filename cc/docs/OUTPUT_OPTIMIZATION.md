# ccnews 输出优化方案 - 极简模式

## 🎯 优化目标

**最大化节约 token，提升阅读效率**

## 📊 对比分析

### v2.0 输出（冗余）

```
📁 2025-10-13/
├── index.html (40KB+)           ❌ 包含大量重复的 CSS/JS
│   ├── 完整的版本说明
│   ├── 5 个热门功能详细描述
│   ├── 8 个技巧完整说明
│   ├── 4 篇文章详细摘要
│   ├── 5 个社区热点完整分析
│   └── 嵌入式 CSS (~8KB)
├── community-trends.html (20KB) ❌ 大量重复内容
├── QUICK_VIEW.md (4KB)          ❌ 包含详细说明
├── README.md (4KB)
└── details/ (多个文件)          ❌ 详细内容分散
```

**问题**：
- 每个 HTML 文件都包含完整的 CSS（8KB+）
- 重复显示历史内容（热门功能、技巧每次都重复）
- 详细的文章摘要（每篇 200+ 字）
- 大量的说明文字和分析

**token 消耗**：~50,000+ tokens（生成所有文件）

### v2.1 极简输出（优化）

```
📁 2025-10-13/
├── index.html (5KB)             ✅ 极简，外部 CSS
│   ├── 今日要点（3 行）
│   ├── 新文章列表（仅标题+链接）
│   ├── 新 Issue 列表（仅标题+链接）
│   └── 热门讨论（仅标题+链接）
└── DAILY.md (2KB)               ✅ 纯文本版

📁 cc/styles/
└── minimal.css (3KB)            ✅ 所有页面共享
```

**优势**：
- CSS 外部化，所有页面共享（节约 ~8KB × 文件数）
- 仅显示变化内容（跳过历史功能和技巧）
- 不生成文章摘要（仅标题+链接）
- 不生成详细分析（仅核心动态）

**token 消耗**：~5,000 tokens（减少 90%）

## 📋 极简输出示例

### index.html（极简版）

```html
<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Daily - 2025-10-14</title>
    <link rel="stylesheet" href="../styles/minimal.css">
</head>
<body>
    <h1>Claude Code 今日简报</h1>
    <p>2025-10-14</p>

    <!-- 今日要点 -->
    <section>
        <h2>🎯 今日要点</h2>
        <ul>
            <li>🆕 v2.0.15 发布</li>
            <li>📚 3 篇新文章</li>
            <li>💬 5 个新 Issue</li>
        </ul>
    </section>

    <!-- 官方更新 -->
    <section>
        <h2>🆕 官方更新</h2>
        <p><strong>v2.0.15</strong> (2025-10-14)</p>
        <ul>
            <li>新功能：自定义代理配置</li>
            <li>Bug 修复：Windows 路径问题</li>
        </ul>
        <a href="https://claudelog.com/...">完整更新日志 →</a>
    </section>

    <!-- 新文章 -->
    <section>
        <h2>📚 新文章 (3)</h2>
        <ul>
            <li><a href="https://...">如何用 Claude Code 构建全栈应用</a> 🆕</li>
            <li><a href="https://...">Claude Code 性能优化指南</a> 🆕</li>
            <li><a href="https://...">MCP 服务器集成实践</a> 🆕</li>
        </ul>
    </section>

    <!-- 新 Issue -->
    <section>
        <h2>🔥 新 Issue (5)</h2>
        <ul>
            <li><a href="https://...">#3510 安装失败问题</a> (2025-10-14)</li>
            <li><a href="https://...">#3511 性能问题</a> (2025-10-14)</li>
            <li>...</li>
        </ul>
    </section>

    <footer>
        <p>📅 2025-10-14 | 🤖 ccnews v2.1</p>
    </footer>
</body>
</html>
```

**大小**：~5KB（vs 40KB）

### DAILY.md（极简版）

```markdown
# Claude Code 今日简报 2025-10-14

## 🎯 今日要点

- 🆕 v2.0.15 发布
- 📚 3 篇新文章
- 💬 5 个新 Issue

## 🆕 官方更新

**v2.0.15** (2025-10-14)
- 新功能：自定义代理配置
- Bug 修复：Windows 路径问题

[完整更新日志](https://claudelog.com/...)

## 📚 新文章 (3)

1. [如何用 Claude Code 构建全栈应用](https://...) 🆕
2. [Claude Code 性能优化指南](https://...) 🆕
3. [MCP 服务器集成实践](https://...) 🆕

## 🔥 新 Issue (5)

- [#3510 安装失败问题](https://...) (2025-10-14)
- [#3511 性能问题](https://...) (2025-10-14)
- ...

---

📅 2025-10-14 | [文档站](https://cc.deeptoai.com/docs)
```

**大小**：~2KB（vs 4KB）

## 🎨 设计原则

### 1. 仅链接，不重复
- ✅ 显示文章标题 + 链接
- ❌ 不生成文章摘要
- ❌ 不重复功能说明
- ❌ 不重复技巧内容

### 2. CSS 外部化
- ✅ 所有 HTML 共享 `../styles/minimal.css`
- ❌ 不在每个文件中嵌入 CSS

### 3. 聚焦变化
- ✅ 仅显示新内容（新文章、新 Issue、新讨论）
- ❌ 不显示历史内容
- ❌ 不显示未变化的功能列表

### 4. 减少文件
- ✅ 仅生成 2 个文件：index.html + DAILY.md
- ❌ 不生成 community-trends.html
- ❌ 不生成 details/ 子目录
- ❌ 不生成 QUICK_VIEW.md（与 DAILY.md 合并）

## 📈 性能提升

| 指标 | v2.0 | v2.1 极简 | 改进 |
|------|------|----------|------|
| **生成文件数** | 7+ 个 | 2 个 | ↓ 70% |
| **单文件大小** | 40KB | 5KB | ↓ 88% |
| **总大小** | ~80KB | ~7KB | ↓ 91% |
| **token 消耗** | 50K+ | 5K | ↓ 90% |
| **阅读时间** | 15 分钟 | 3 分钟 | ↓ 80% |
| **CSS 重复** | 每文件 8KB | 共享 3KB | ↓ 95% |

## 🔧 配置选项

### config.json

```json
{
  "output": {
    "layout": "minimal",           // 使用极简布局
    "externalCSS": true,            // CSS 外部化
    "includeSubdirectories": false  // 不生成子目录
  },
  "display": {
    "focusOnChanges": true,              // 聚焦变化
    "showOnlyLinks": true,               // 仅显示链接
    "skipArticleSummaries": true,        // 跳过文章摘要
    "skipFeatureDescriptions": true,     // 跳过功能描述
    "skipDetailedAnalysis": true,        // 跳过详细分析
    "maxNewArticles": 10,                // 最多 10 篇新文章
    "maxNewIssues": 10,                  // 最多 10 个新 Issue
    "maxHotDiscussions": 5               // 最多 5 个热门讨论
  }
}
```

## 🚀 使用方式

### 第一次运行（初始化）
```bash
/ccnews
```
生成：
- `cache/` - 创建缓存
- `2025-10-14/index.html` - 完整报告（首次）
- `2025-10-14/DAILY.md` - Markdown 版本

### 后续运行（极简模式）
```bash
/ccnews
```
生成：
- `2025-10-15/index.html` - 仅新内容（5KB）
- `2025-10-15/DAILY.md` - 仅新内容（2KB）

### 查看方式
```bash
# 浏览器查看
open 2025-10-15/index.html

# 终端查看
cat 2025-10-15/DAILY.md

# 或直接在 Claude Code 中打开
```

## 💡 实现建议

### 生成逻辑

```javascript
// 伪代码
function generateMinimalReport(changes) {
  const html = `
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="../styles/minimal.css">
</head>
<body>
    <h1>Claude Code 今日简报</h1>
    <p>${date}</p>

    ${changes.hasOfficialUpdate ? renderOfficialUpdate(changes.version) : ''}

    ${changes.newArticles.length > 0 ? renderNewArticles(changes.newArticles) : ''}

    ${changes.newIssues.length > 0 ? renderNewIssues(changes.newIssues) : ''}

    <footer>📅 ${date} | 🤖 ccnews v2.1</footer>
</body>
</html>
  `

  // 渲染函数只生成标题+链接，不生成摘要
  function renderNewArticles(articles) {
    return `
<section>
    <h2>📚 新文章 (${articles.length})</h2>
    <ul>
        ${articles.map(a => `<li><a href="${a.url}">${a.title}</a> 🆕</li>`).join('')}
    </ul>
</section>
    `
  }

  // 其他渲染函数类似...
}
```

### 缓存对比

```javascript
// 伪代码
function detectChanges(cached, current) {
  return {
    hasOfficialUpdate: current.version !== cached.version,
    newArticles: current.articles.filter(a =>
      !cached.articles.find(ca => ca.url === a.url)
    ),
    newIssues: current.issues.filter(i =>
      new Date(i.createdAt) > new Date(cached.lastCheckDate)
    )
  }
}
```

## 📝 实际输出对比

### 完整版（v2.0）
```
index.html:
  - CSS: 8KB
  - 版本说明: 2KB
  - 热门功能: 5KB
  - 实用技巧: 6KB
  - 文章摘要: 8KB
  - 社区分析: 10KB
  - 其他: 1KB
  总计: 40KB

community-trends.html: 20KB
QUICK_VIEW.md: 4KB
...
总计: ~80KB
```

### 极简版（v2.1）
```
index.html:
  - 今日要点: 0.3KB
  - 新文章链接: 0.5KB
  - 新 Issue 链接: 0.8KB
  - 热门讨论: 0.4KB
  - 其他: 0.5KB
  总计: 5KB

DAILY.md: 2KB
总计: ~7KB
```

**节约比例**：91%

## ✅ 优势总结

1. **token 节约 90%**：从 50K 降到 5K
2. **文件减少 70%**：从 7+ 个降到 2 个
3. **大小减少 91%**：从 80KB 降到 7KB
4. **阅读时间减少 80%**：从 15 分钟降到 3 分钟
5. **维护简单**：仅 2 个文件，1 个 CSS

## 🎯 核心理念

> **每日简报的本质是快速了解变化，而不是重复阅读历史内容**

- 用户只需要知道："今天有什么新东西？"
- 标题和链接已足够，详细内容点击链接查看
- 历史功能和技巧不需要每天重复
- CSS 应该共享，不应该在每个文件中重复

---

📅 创建时间：2025-10-13
🎯 优化目标：减少 90% token 消耗
✅ 设计状态：已完成
