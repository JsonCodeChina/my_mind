# Claude Code 今日变化 - {{date}}

> 3分钟快速了解今日核心动态

## 📌 一句话总结

{{oneSentenceSummary}}

---

## 🎯 今日亮点

{{#hasOfficialUpdate}}
### 🆕 官方发布 v{{newVersion}}（{{releaseDate}}）
{{#topFeatures}}
- {{feature}}
{{/topFeatures}}
[完整更新日志]({{changelogUrl}})
{{/hasOfficialUpdate}}

{{#hasNewArticles}}
### 📚 新文章（{{newArticlesCount}} 篇）
{{#newArticles}}
{{index}}. **{{title}}** - {{oneSentenceSummary}} [链接]({{url}})
{{/newArticles}}
{{/hasNewArticles}}

{{#hasHotCommunityTopics}}
### 🔥 社区热点
{{#hotTopics}}
- **{{title}}**（{{source}}，{{engagement}}）- {{summary}} [链接]({{url}})
{{/hotTopics}}
{{/hasHotCommunityTopics}}

---

## 📊 快速统计

```
新版本：{{hasOfficialUpdate ? 'v' + newVersion : '无'}}
新文章：{{newArticlesCount}} 篇
新 Issue：{{newIssuesCount}} 个
热门讨论：{{hotDiscussionsCount}} 个
```

---

## 🔗 推荐阅读（TOP 3）

{{#topRecommendations}}
{{index}}. {{title}} - {{reason}}
   [阅读]({{url}})
{{/topRecommendations}}

---

📅 {{generatedAt}} | [查看详细报告](./index.html) | [完整文章目录](./FULL_CATALOG.md)
