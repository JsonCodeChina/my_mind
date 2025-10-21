# AI 动态全景报告

生成覆盖整个 AI 领域的动态简报，包括：

1. **模型动态**：LMSYS 排行榜、新模型发布
2. **行业新闻**：AI 领域重要新闻和公告
3. **社区讨论**：Reddit、Hacker News 热议话题
4. **开发工具**：Claude Code、Cursor 等 AI 编程工具动态

---

请启动 ainews-analyst agent（位于 `.claude/agents/ainews-analyst.md`），按照以下流程生成报告：

## 第 1 步：数据采集

### 1.1 模型排名
使用 WebFetch 读取：
- LMSYS Chatbot Arena: https://chat.lmsys.org/

提取信息：
- Top 5 模型排名和 ELO 分数
- 近期排名变化

### 1.2 AI 社区讨论
使用 WebFetch 读取：
- Reddit r/artificial: https://www.reddit.com/r/artificial/
- Reddit r/LocalLLaMA: https://www.reddit.com/r/LocalLLaMA/
- Hacker News AI 话题：https://news.ycombinator.com/

提取信息：
- 热门帖子（>100 upvotes/points）
- 关键讨论话题

### 1.3 官方动态
使用 WebFetch 读取：
- Anthropic Blog: https://www.anthropic.com/news
- OpenAI Blog: https://openai.com/blog

提取信息：
- 最新 1-2 篇文章标题和摘要

### 1.4 开发工具动态
读取现有数据：
- `cc/.meta/cache/daily_data.json`（Claude Code 数据）

提取信息：
- Top 3 热门 Issues
- 社区关键反馈

---

## 第 2 步：AI 分析

综合所有数据源，生成一份 **80-120 行**的 AI 动态报告，包含：

1. **📊 模型动态**（15-20 行）
   - 排行榜 Top 5
   - 排名变化趋势
   - 新模型发布

2. **📰 行业新闻**（20-30 行）
   - 官方博客最新动态
   - 重要产品更新
   - 行业趋势

3. **🔥 社区热议**（25-35 行）
   - Reddit 热门话题（3-5 个）
   - HN 讨论要点
   - 社区情绪分析

4. **🛠️ 开发工具动态**（20-30 行）
   - Claude Code 热门 Issues
   - Cursor/Windsurf 动态（如有）
   - 工具对比和趋势

---

## 第 3 步：生成报告

输出文件：`ainews/YYYY-MM-DD/index.md`（使用今天日期）

报告风格：
- 客观、数据驱动
- 引用原文（帖子标题、评论）
- 标注来源和热度数据
- 简洁但信息丰富

---

## 性能目标

- **总耗时**：< 60 秒
- **Token 消耗**：12-18K
- **报告长度**：80-120 行
- **数据源**：4-6 个

---

开始执行！
