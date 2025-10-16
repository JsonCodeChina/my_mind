# ccnews 优化项目 - 技术可行性调研报告

**调研日期**: 2025-10-14
**调研目标**: 验证 Python 数据采集方案的技术可行性
**调研状态**: ✅ 完成

---

## 执行摘要

本次调研验证了使用 Python 脚本进行数据采集的技术可行性。**所有关键数据源均可访问且数据质量良好**，可以支持高效、低成本的自动化数据采集系统。

**核心结论：**
- ✅ GitHub API: 可用，数据完整，无需认证即可使用（60次/小时）
- ✅ HN Algolia API: 可用，数据完整，搜索功能强大
- ✅ 社区文档站: 可爬取，包含发布日期元数据
- ✅ 数据结构设计完成，支持所有业务需求
- ✅ 热度评分算法定义清晰，可直接实现

**推荐行动**: 进入阶段 1 - 开发 Python 数据采集脚本

---

## 1. GitHub API 测试结果

### 1.1 API 可用性

**测试 API**: `https://api.github.com/repos/anthropics/claude-code/issues`

**测试结果**: ✅ 成功

**Rate Limit**:
- 未认证: 60 次/小时
- 已认证: 5000 次/小时
- **结论**: 未认证足够日常使用（每天只需 1-2 次调用）

### 1.2 返回数据质量

**测试样本**: Issue #5037

**数据完整性**: 优秀
```json
{
  "number": 5037,
  "title": "MCP servers in .claude/.mcp.json not loading properly",
  "html_url": "https://github.com/anthropics/claude-code/issues/5037",
  "state": "open",
  "comments": 12,
  "reactions": {
    "total_count": 11,
    "+1": 10,
    "-1": 0,
    "laugh": 0,
    "hooray": 1,
    ...
  },
  "labels": [
    {"name": "bug"},
    {"name": "has repro"},
    {"name": "platform:linux"},
    {"name": "area:mcp"}
  ],
  "created_at": "2025-08-03T11:02:21Z",
  "updated_at": "2025-10-14T13:00:23Z"
}
```

**可用字段**:
- ✅ Issue 编号、标题、链接
- ✅ 评论数量
- ✅ Reactions 详细数据（总数 + 分类）
- ✅ 标签（bug, feature, priority 等）
- ✅ 创建时间、更新时间
- ✅ 状态（open/closed）

### 1.3 筛选策略

**当前方案**:
```
GET /repos/anthropics/claude-code/issues?state=all&sort=updated&per_page=50
```

**优化建议**:
- 获取最近 3-7 天更新的 Issues（使用 `since` 参数）
- 在本地按热度评分排序
- 过滤掉 heat_score < 20 的 Issues

**预计效率**: 1 次 API 调用，< 2 秒

---

## 2. Hacker News API 测试结果

### 2.1 API 可用性

**测试 API**: `https://hn.algolia.com/api/v1/search`

**测试结果**: ✅ 成功

**Rate Limit**: 无明确限制（Algolia 免费层，足够使用）

### 2.2 返回数据质量

**测试样本**: "Claude 3.7 Sonnet and Claude Code"

**数据完整性**: 优秀
```json
{
  "objectID": "43163011",
  "title": "Claude 3.7 Sonnet and Claude Code",
  "url": "https://www.anthropic.com/news/claude-3-7-sonnet",
  "points": 2127,
  "num_comments": 963,
  "author": "bakugo",
  "created_at": "2025-02-24T18:28:59Z",
  "created_at_i": 1740421739
}
```

**可用字段**:
- ✅ Story ID (objectID)
- ✅ 标题、链接
- ✅ 分数 (points)
- ✅ 评论数 (num_comments)
- ✅ 作者
- ✅ 创建时间（字符串 + Unix 时间戳）

### 2.3 搜索策略

**搜索参数**:
```
query=Claude Code
tags=story
numericFilters=created_at_i>[7天前时间戳]
```

**优化建议**:
- 搜索 "Claude Code" 关键词
- 限制为 story 类型（排除评论）
- 按时间过滤（最近 7 天）
- 在本地按热度评分排序

**预计效率**: 1 次 API 调用，< 2 秒

---

## 3. 社区文档站分析结果

### 3.1 站点结构

**主站**: https://cc.deeptoai.com/docs

**文章分类**:
1. Best Practices (最佳实践)
2. Community Tips (社区技巧)
3. Tools (工具)
4. Advanced Techniques (高级技巧)

### 3.2 元数据可用性

**测试页面**: https://cc.deeptoai.com/docs/zh/best-practices/claude-code-best-practices

**元数据**: ✅ 包含发布日期
```
Publish Date: April 18, 2025
```

**数据提取方式**:
1. 从首页获取所有文章链接
2. 使用 BeautifulSoup 提取文章列表
3. 对于候选文章，请求页面提取发布日期
4. 按日期和分类评分

### 3.3 爬取策略

**两阶段方案**:
1. **快速扫描**: 获取所有文章标题和链接（从首页）
2. **选择性详细爬取**: 只爬取符合初步筛选的文章（最多 5-10 篇）

**HTML 结构**:
- 文章链接: `<a>` 标签，包含文章路径
- 分类: 从 URL 路径提取 (`/best-practices/`, `/community-tips/`)
- 发布日期: 页面 meta 标签或正文

**预计效率**: 1 次首页请求 + 3-5 次文章页面请求，< 5 秒

---

## 4. 数据结构设计

### 4.1 输出格式

**文件**: `cc/cache/daily_data.json`

**结构**: 见 `cc/schemas/daily_data.schema.json`

**核心部分**:
```json
{
  "metadata": {
    "timestamp": "2025-10-14T10:00:00Z",
    "date": "2025-10-14",
    "version": "1.0"
  },
  "version": {
    "current": "v2.0.14",
    "release_date": "2025-10-11",
    "is_new": false
  },
  "issues": [
    {
      "number": 5037,
      "title": "...",
      "url": "...",
      "comments": 12,
      "reactions": 11,
      "heat_score": 61.5,
      "labels": ["bug", "has repro"],
      "created_at": "2025-08-03T11:02:21Z"
    }
  ],
  "discussions": [...],
  "articles": [...]
}
```

### 4.2 设计原则

1. **完整性**: 包含所有必要字段，支持热度计算
2. **扩展性**: 易于添加新字段或数据源
3. **标准化**: 使用 ISO 8601 时间格式
4. **可读性**: JSON 格式，易于人工检查

---

## 5. 热度评分算法

### 5.1 算法设计

详细文档见 `cc/docs/heat-algorithm.md`

**核心公式**:

**GitHub Issues**:
```
heat_score = (comments × 2) + (reactions × 1.5) + time_bonus + label_bonus
```

**Hacker News**:
```
heat_score = (points × 1.5) + (comments × 2) + time_bonus + relevance_bonus
```

**文章质量**:
```
quality_score = recency_score + category_score + keyword_score + length_score
```

### 5.2 阈值设置

| 类型 | 高 | 中 | 低 |
|------|----|----|------|
| Issues | ≥50 | ≥20 | <20 |
| HN讨论 | ≥100 | ≥50 | <50 |
| 文章 | ≥70 | ≥50 | <50 |

**筛选标准**:
- Issues: TOP 5（heat_score ≥ 20）
- HN讨论: TOP 3（heat_score ≥ 50）
- 文章: 1-2 篇（quality_score ≥ 70）

---

## 6. 性能预估

### 6.1 执行时间

| 步骤 | 预计耗时 | 备注 |
|------|----------|------|
| GitHub API 调用 | 1-2 秒 | 1 次请求，50 条数据 |
| HN API 调用 | 1-2 秒 | 1 次搜索请求 |
| 版本检测 | 0.5-1 秒 | 简单 HTTP 请求 |
| 社区文档站爬取 | 3-5 秒 | 1 次首页 + 3-5 次文章页面 |
| 数据处理和排序 | <1 秒 | 本地计算 |
| JSON 序列化 | <0.5 秒 | 写入文件 |
| **总计** | **7-12 秒** | vs 当前 45 秒 |

**性能提升**: 73-85%

### 6.2 Token 消耗

| 阶段 | 当前方案 | 新方案 | 节省 |
|------|----------|--------|------|
| 数据采集 | 15-25k tokens | 0 tokens | 100% |
| 数据分析 | 5-10k tokens | 5-8k tokens | 20-40% |
| 报告生成 | 5-10k tokens | 3-5k tokens | 40-60% |
| **总计** | **25-45k tokens** | **8-13k tokens** | **71-82%** |

**成本节省**: 70-80%

---

## 7. 技术栈选择

### 7.1 Python 依赖

**必需库**:
```python
requests         # HTTP 请求
beautifulsoup4   # HTML 解析
python-dateutil  # 日期处理
```

**可选库**:
```python
requests-cache   # API 响应缓存（避免重复请求）
tenacity         # 重试机制
```

### 7.2 兼容性

- ✅ Python 3.8+
- ✅ macOS / Linux / Windows (WSL)
- ✅ 无需额外系统依赖

---

## 8. 风险评估

### 8.1 潜在风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| GitHub API rate limit | 低 | 中 | 使用缓存，添加认证 token |
| 网络请求失败 | 中 | 低 | 重试机制，使用上次缓存 |
| 社区站结构变化 | 低 | 中 | 添加 HTML 结构验证 |
| HN API 不稳定 | 低 | 低 | 降级为不显示 HN 数据 |

### 8.2 降级策略

**原则**: 任何单个数据源失败不应影响整体运行

**实现**:
1. 每个数据源独立异常处理
2. 失败时使用缓存数据（如果可用）
3. 在报告中标注数据源状态

---

## 9. 下一步行动

### 9.1 阶段 1：Python 脚本开发

**目标**: 实现稳定可靠的数据采集脚本

**任务清单**:
1. ✅ 调研完成（当前阶段）
2. ⏸️ 创建 `cc/scripts/fetch_data.py`
3. ⏸️ 实现 GitHub Issues 爬取
4. ⏸️ 实现 HN 讨论爬取
5. ⏸️ 实现社区文档爬取
6. ⏸️ 实现版本检测
7. ⏸️ 实现热度评分算法
8. ⏸️ 添加错误处理和重试机制
9. ⏸️ 编写单元测试
10. ⏸️ 文档和使用说明

**预计时间**: 2-3 小时

### 9.2 验收标准

**功能要求**:
- ✅ 成功获取所有数据源
- ✅ 输出符合 schema 定义
- ✅ 执行时间 < 15 秒
- ✅ 数据准确性 > 95%

**质量要求**:
- ✅ 代码可读性好，有注释
- ✅ 错误处理完善
- ✅ 日志输出清晰
- ✅ 可独立测试

---

## 10. 结论

### 10.1 核心发现

1. **技术可行性**: 100% 可行，所有 API 均可访问
2. **性能优势**: 速度提升 73-85%，成本降低 70-80%
3. **数据质量**: 所有数据源质量优秀，满足需求
4. **实现复杂度**: 低，预计 2-3 小时完成开发

### 10.2 推荐决策

**强烈推荐采用 Python 数据采集方案**

**理由**:
- ✅ 性能显著提升
- ✅ 成本大幅降低
- ✅ 数据质量更可控
- ✅ 易于维护和扩展
- ✅ 技术风险低

### 10.3 投资回报

**一次性投资**: 2-3 小时开发时间

**持续收益**:
- 每次运行节省 30-35 秒
- 每次节省 15-30k tokens（~$0.03-0.06）
- 每天运行 1 次，每月节省约 $0.9-1.8
- 更重要的是：更快的执行速度和更好的用户体验

---

## 附录

### A. 测试命令记录

**GitHub API**:
```bash
curl "https://api.github.com/repos/anthropics/claude-code/issues?state=all&sort=updated&per_page=10"
curl "https://api.github.com/rate_limit"
```

**HN API**:
```bash
curl "https://hn.algolia.com/api/v1/search?query=Claude%20Code&tags=story"
```

### B. 相关文档

- [GitHub REST API 文档](https://docs.github.com/en/rest)
- [HN Algolia API 文档](https://hn.algolia.com/api)
- [数据结构定义](../schemas/daily_data.schema.json)
- [热度评分算法](../docs/heat-algorithm.md)

---

**报告状态**: ✅ 完成
**下一步**: 进入阶段 1 - Python 脚本开发
**负责人**: ccnews 优化项目团队
**审核人**: 待定
