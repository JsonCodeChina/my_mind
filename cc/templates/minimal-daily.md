# Claude Code 今日简报 {{date}}

> 极简版 - 仅显示标题和链接，节约 token

---

## 🎯 今日要点

{{#hasOfficialUpdate}}
- 🆕 **官方** v{{newVersion}} 发布
{{/hasOfficialUpdate}}
{{^hasOfficialUpdate}}
- 📌 **官方** 无更新
{{/hasOfficialUpdate}}
- 📚 **文章** {{newArticlesCount}} 篇新增
- 💬 **讨论** {{newIssuesCount}} 个新 Issue
- 🔥 **热点** {{hotTopicsCount}} 个话题

---

{{#hasOfficialUpdate}}
## 🆕 官方更新

**v{{newVersion}}** ({{releaseDate}})
{{#changelogItems}}
- {{item}}
{{/changelogItems}}

[完整更新日志]({{changelogUrl}})

---
{{/hasOfficialUpdate}}

{{#hasNewArticles}}
## 📚 新文章 ({{newArticlesCount}})

{{#newArticles}}
{{index}}. [{{title}}]({{url}}) 🆕
{{/newArticles}}

---
{{/hasNewArticles}}

{{#hasUpdatedArticles}}
## 🔄 文章更新 ({{updatedArticlesCount}})

{{#updatedArticles}}
- [{{title}}]({{url}}) ({{lastModified}})
{{/updatedArticles}}

---
{{/hasUpdatedArticles}}

{{#hasNewIssues}}
## 🔥 新 Issue ({{newIssuesCount}})

{{#newIssues}}
- [#{{number}} {{title}}]({{url}}) ({{createdAt}})
{{/newIssues}}

---
{{/hasNewIssues}}

{{#hasHotDiscussions}}
## 💬 热门讨论

{{#hotDiscussions}}
- [{{title}}]({{url}}) ({{engagement}})
{{/hotDiscussions}}

---
{{/hasHotDiscussions}}

## 📊 统计

```
新文章：{{newArticlesCount}}
更新文章：{{updatedArticlesCount}}
新 Issue：{{newIssuesCount}}
热门讨论：{{hotDiscussionsCount}}
```

---

📅 {{generatedAt}} | [详细版](./index.html) | [文档站](https://cc.deeptoai.com/docs)
