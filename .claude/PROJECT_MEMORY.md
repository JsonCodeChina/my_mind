# AINews 项目记忆

## 核心信息

- **当前**: AI 生态监控系统 v3.0-ai
- **路径**: `/Users/shenbo/Desktop/mind/cc`
- **功能**: ✅ 多产品（Claude Code + Cursor）、✅ 多关键词新闻、🔜 模型排名
- **脚本**: `fetch_ai_data.py` (9秒抓取2产品+5新闻)

## 用户需求（关键点）

### 扩展目标
- **AI 工具**: Cursor, Copilot, Windsurf
- **AI 模型**: OpenAI (GPT-4/o1), Gemini, Llama, DeepSeek
- **排名**: LMSYS Arena, HuggingFace Leaderboard
- **新闻**: HN, Reddit (r/MachineLearning, r/ClaudeAI), ArXiv

### 技术要求
- ✅ **MCP 工具**: Firecrawl (后期集成)
- ✅ **效率优先**: 减少 token 浪费，先优化现有流程
- ✅ **项目记忆**: 避免重复沟通

## 用户偏好
- **开发**: 分阶段、先优化现有、保留功能、高效简洁
- **报告**: 100-250行、引用评论、数据驱动、情感分析
- **技术**: Python + SQLite + Firecrawl MCP（后期）

## 技术决策

### 数据采集
- **现在**: requests + BeautifulSoup + GitHub API
- **未来**: Firecrawl MCP（LMSYS Arena 等 JS 渲染网站）

### 数据库（SQLite）
- **现有**: issues, comments, discussions, versions
- **计划**: products, models, rankings, news

## 重要约束
- ❌ 不删除现有功能
- ❌ 不牺牲报告质量
- ❌ 不过度优化（先功能后性能）
- ❌ 不生成超长文档（浪费token）
- ✅ 报告 100-250 行
- ✅ 抓取 < 90 秒

## 下一步
1. 测试 Firecrawl MCP（是否已安装可用）
2. 优化现有流程（减少重复抓取）
3. 扩展到多产品（渐进式）

---
**更新**: 2025-10-16 | **维护**: 每次讨论后精简更新
