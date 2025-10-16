# Claude Code 日报 - {{date}}

## 📦 版本
**{{version}}**{{#isNew}} 🆕{{/isNew}} ({{releaseDate}})

## 🔥 热门 Issues

{{#issues}}
### #{{number}} - {{title}}
**热度**: {{heatScore}} | **评论**: {{comments}} | **反应**: {{reactions}} | **状态**: {{state}}
**核心**: {{oneLinerSummary}}
[查看详情]({{url}})

---

{{/issues}}

{{^hasIssues}}
_今日无重大Issues_
{{/hasIssues}}

## 💬 HN 讨论

{{#discussions}}
**{{title}}** (↑{{points}} 💬{{comments}})
{{valueProp}}
[HN讨论]({{hnUrl}})

{{/discussions}}

{{^hasDiscussions}}
_今日无热门讨论_
{{/hasDiscussions}}

## 📊 社区脉搏

**情绪**: {{emotion}} {{emotionReason}}
**焦点**: {{focus}}
**趋势**: {{trend}}

---

**数据**: GitHub ({{issueCount}} issues) | HN ({{discussionCount}} discussions)
**生成**: {{timestamp}}
