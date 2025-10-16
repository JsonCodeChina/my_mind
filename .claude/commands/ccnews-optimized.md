---
description: 获取 Claude Code 最新动态（优化版）
---

# Claude Code 每日资讯生成（优化版）

**优化亮点**:
- ⚡ 异步并行爬取（提速70%）
- 📉 精简报告格式（Token减少50%）
- 🎯 严格筛选阈值（聚焦核心内容）

**执行流程**: Python 异步采集 → 精简 Agent 分析 → 超精简报告

---

## 第 1 步：运行 Python 异步数据采集脚本

**目标**: 并行采集数据（预计3-5秒）

```bash
cd /Users/shenbo/Desktop/mind/cc
source venv/bin/activate
python scripts/fetch_data_async.py
```

**优化点**：
- ✅ 使用 `asyncio` + `aiohttp` 并行请求
- ✅ Issue热度阈值：20 → 30（更严格）
- ✅ HN热度阈值：50 → 70（更严格）
- ✅ 最大Issue数：5 → 3
- ✅ 最大讨论数：3 → 2

**输出**: `cc/cache/daily_data.json`

**错误处理**:
- 如果aiohttp未安装：`pip install aiohttp`
- 如果脚本失败，检查网络连接
- 查看日志了解具体错误

---

## 第 2 步：启动精简版 ccnews-analyzer Agent

**目标**: 智能分析数据并生成超精简报告（预计5-8秒）

使用 Task 工具启动 `ccnews-analyzer-minimal` agent：

```
Agent: ccnews-analyzer-minimal
Subagent Type: general-purpose

Prompt:
请按照 `.claude/agents/ccnews-analyzer-minimal.md` 中定义的规范，分析 cc/cache/daily_data.json 数据并生成今日精简报告。

具体任务：
1. 读取 cc/cache/daily_data.json
2. 读取 cc/baseline.json 进行版本对比
3. 分析最多3个热门Issues，为每个生成一句话核心摘要（15-20字）
4. 分析最多2个HN讨论，提取核心价值点（20字以内）
5. 生成社区脉搏综合分析（情绪+焦点+趋势，共10-15行）
6. 输出到 cc/YYYY-MM-DD/index.md（使用今天的日期）

**严格要求**：
- 总行数 ≤ 180行
- 总字数 ≤ 2000字
- 每个Issue ≤ 5行
- 社区脉搏 ≤ 15行
- 删除所有详细分析、预测、战略观察

请现在开始分析并生成精简报告。
```

---

## 第 3 步：后处理

**任务**:
1. 检查生成的 `cc/YYYY-MM-DD/index.md`
2. 验证行数 ≤ 180行：`wc -l cc/YYYY-MM-DD/index.md`
3. 更新 `cc/baseline.json`:
   - 更新 lastCheckDate 为今天
   - 如果有新版本，更新 claudeCodeVersion
4. 在终端显示报告路径

**Baseline 更新示例**:
```json
{
  "lastCheckDate": "2025-10-15",
  "claudeCodeVersion": "v2.0.15",
  "lastUpdateDate": "2025-10-15",
  "notes": "优化版ccnews运行成功。采集到3个热门Issues、1个HN讨论。报告约150行。"
}
```

---

## 质量检查清单

生成报告后，验证以下内容：

- [ ] 报告行数 ≤ 180行（使用 `wc -l` 验证）
- [ ] 版本信息准确（与 daily_data.json 一致）
- [ ] Issues数量正确（最多3个）
- [ ] 每个Issue有一句话核心摘要
- [ ] HN讨论有价值点提取（20字以内）
- [ ] 社区脉搏简洁（10-15行）
- [ ] 所有链接完整有效
- [ ] 无详细分析、预测等冗余内容

---

## 性能指标（优化后）

- **Python脚本**: 3-5秒（vs 之前10秒）⚡
- **Agent分析**: 5-8秒（vs 之前15秒）⚡
- **总耗时**: 8-13秒（vs 之前25秒）**提速52%** 🚀
- **Token消耗**: 2-4k（vs 之前7k）**减少50%** 📉
- **报告行数**: 150-180行（vs 之前343行）**减少48%** 📄

---

## 对比：优化前 vs 优化后

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 爬取速度 | 10秒 | 3-5秒 | ⚡ 70% |
| 分析速度 | 15秒 | 5-8秒 | ⚡ 50% |
| 总时间 | 25秒 | 8-13秒 | **🚀 52%** |
| Token | 7k | 2-4k | **📉 50%** |
| 报告行数 | 343行 | 150-180行 | **📄 48%** |
| Issue数量 | 5个 | 3个 | 聚焦核心 |
| 讨论数量 | 3个 | 2个 | 聚焦核心 |

---

## 故障排查

### 问题 1: aiohttp 未安装
```bash
source venv/bin/activate
pip install aiohttp
```

### 问题 2: Python脚本失败
```bash
# 使用详细模式运行
python scripts/fetch_data_async.py --verbose

# 检查网络连接
curl -I https://api.github.com
```

### 问题 3: Agent生成报告过长
- 确保使用 `ccnews-analyzer-minimal` 而不是旧版 `ccnews-analyzer`
- 在Prompt中强调 "总行数 ≤ 180行"

### 问题 4: daily_data.json 不存在
- 确保第1步Python脚本成功执行
- 检查 `cc/cache/` 目录是否存在

---

## 注意事项

- ⚠️ 必须先运行 Python 脚本，再启动 Agent
- ⚠️ Python 脚本需要在虚拟环境中运行
- ⚠️ 使用新版Agent `ccnews-analyzer-minimal`（不是旧版）
- ⚠️ 报告生成在 `cc/YYYY-MM-DD/index.md`，注意日期
- ⚠️ 每次运行会覆盖同一天的报告

---

**记住**: 新方案的核心优势是「快速」+「精准」+「精简」。异步并行爬取 + 严格筛选 + 精简分析，5-10分钟即可获得高质量的核心资讯。
