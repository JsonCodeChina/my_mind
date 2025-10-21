# 技术决策记录

> 核心技术决策，简洁记录

---

## ADR-001: Firecrawl MCP 集成

**工具**: Firecrawl MCP
**用途**: LMSYS Arena 等 JS 渲染网站
**时机**: 需要时再集成（不是现在）
**降级**: 失败则用 BeautifulSoup

---

## ADR-002: 数据库扩展

**现在**: SQLite (issues, comments, discussions, versions)
**未来**: 新增 products, models, rankings, news 表
**Migration**: 渐进式，保持向后兼容

---

## ADR-003: 异步并发（未来优化）

**目标**: 多产品抓取耗时从 105s → 30s
**方案**: `asyncio` + `aiohttp` + 信号量控制
**时机**: 需要时再做（不是现在）

---

**更新**: 2025-10-16
