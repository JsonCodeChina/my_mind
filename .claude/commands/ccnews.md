---
description: Claude Code 每日深度分析（100 行精品报告）
---

# Claude Code 日报生成

**核心优势**: 评论挖掘 + 趋势分析 + 情感洞察

---

## 第 1 步：数据采集（15-20 秒）

```bash
cd /Users/shenbo/Desktop/mind/cc
source .meta/venv/bin/activate
python .meta/scripts/fetch_data_v2.py
```

**输出**:
- `cc/.meta/cache/daily_data.json` (包含高赞评论)
- 数据自动存入 `cc/ainews.db` (SQLite 数据库)

---

## 第 2 步：AI 分析（10-15 秒）

启动 ccnews-analyst agent:

**Agent**: general-purpose

**Prompt**:
```
请按照 `.claude/agents/ccnews-analyst.md` 的规范分析数据并生成报告。

任务：
1. 读取 cc/.meta/cache/daily_data.json
2. 从每个 Issue 的 top_comments 中选出最有价值的 5-10 条评论
3. 分析 trend 数据（热度变化、评论增速）
4. 基于评论判断社区情绪（引用原文证明）
5. 生成 100 行左右报告（弹性 80-120）

输出：cc/2025-10-16/index.md (使用今天日期)

重点：
- 必须包含社区高赞评论（标注作者和点赞数）
- 必须包含趋势数据（↑↓ 和具体数字）
- 必须基于数据预测（引用 prediction 字段）
- 保持客观但不失趣味性

开始分析。
```

---

## 第 3 步：后处理

1. 检查报告行数：`wc -l cc/2025-10-16/index.md`
2. 更新 cc/.meta/baseline.json (lastCheckDate, version)
3. 显示报告路径

---

## 质量标准

- ✅ 包含 5-10 条社区评论
- ✅ 趋势数据完整（↑↓ %）
- ✅ 预测有数据支撑
- ✅ 总长 100 行左右（80-120）

---

## 性能指标

- **数据采集**: 15-20 秒（含评论抓取）
- **AI 分析**: 10-15 秒
- **总耗时**: ~30 秒
- **Token 消耗**: 6-9k（增加评论分析深度）
- **评论覆盖**: 10-20 条高质量评论

---

**记住**: 核心价值在于**社区对话挖掘**和**趋势预测**，让用户快速了解技术方案和情绪走向。
