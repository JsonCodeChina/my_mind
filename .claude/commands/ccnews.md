---
description: 获取 Claude Code 最新动态
---

# Claude Code 每日资讯生成

**执行流程**: Python 数据采集 → Sub-agent 智能分析 → 生成精简报告

---

## 第 1 步：运行 Python 数据采集脚本

**目标**: 从 GitHub、HN、社区文档站采集数据（5-10 秒）

```bash
cd /Users/shenbo/Desktop/mind/cc
source venv/bin/activate
python scripts/fetch_data.py
```

**输出**: `cc/cache/daily_data.json`

**错误处理**:
- 如果脚本失败，检查网络连接
- 查看日志了解具体错误
- 必要时可以使用 `--verbose` 参数

---

## 第 2 步：启动 ccnews-analyzer Agent

**目标**: 智能分析数据并生成 Markdown 报告

使用 Task 工具启动 ccnews-analyzer agent：

```
Agent: ccnews-analyzer
Subagent Type: general-purpose

Prompt:
请按照 `.claude/agents/ccnews-analyzer.md` 中定义的规范，分析 cc/cache/daily_data.json 数据并生成今日报告。

具体任务：
1. 读取 cc/cache/daily_data.json
2. 读取 cc/baseline.json 进行版本对比
3. 分析 5 个热门 Issues，为每个生成一句话总结
4. 分析 HN 讨论，提取核心价值点
5. 处理文章推荐（如果有）
6. 生成社区脉搏综合分析
7. 输出到 cc/YYYY-MM-DD/index.md（使用今天的日期）

输出格式要求：
- Markdown 格式
- 150-200 行（不含空行）
- 每个 Issue 用 1 句话总结核心问题
- 包含热度、评论数、反应数等关键指标
- 最后附上数据来源统计

请现在开始分析并生成报告。
```

---

## 第 3 步：后处理

**任务**:
1. 检查生成的 `cc/YYYY-MM-DD/index.md`
2. 更新 `cc/baseline.json`:
   - 更新 lastCheckDate 为今天
   - 如果有新版本，更新 claudeCodeVersion
3. 在终端显示报告路径
4. 用 Markdown 阅读器打开报告（可选）

**Baseline 更新示例**:
```json
{
  "lastCheckDate": "2025-10-14",
  "claudeCodeVersion": "v2.0.14",
  "lastUpdateDate": "2025-10-11",
  "notes": "数据采集脚本运行成功。采集到 5 个热门 Issues、1 个 HN 讨论。当前版本 v2.0.14 稳定运行。"
}
```

---

## 质量检查清单

生成报告后，验证以下内容：

- [ ] 版本信息准确（与 daily_data.json 一致）
- [ ] Issues 数量正确（最多 5 个）
- [ ] 每个 Issue 有一句话总结
- [ ] HN 讨论有亮点提取
- [ ] 社区脉搏分析合理
- [ ] 所有链接完整有效
- [ ] 数据来源统计正确
- [ ] Markdown 格式规范

---

## 性能指标

- **Python 脚本**: 5-10 秒
- **Agent 分析**: 10-15 秒
- **总耗时**: 15-25 秒（vs 之前 45 秒）
- **Token 消耗**: 5-8k（vs 之前 25-45k）

---

## 故障排查

### 问题 1: Python 脚本失败
```bash
# 检查虚拟环境
source venv/bin/activate
pip list | grep requests

# 重新安装依赖
pip install -r requirements.txt

# 使用详细模式运行
python scripts/fetch_data.py --verbose
```

### 问题 2: daily_data.json 不存在
- 确保第 1 步成功执行
- 检查 `cc/cache/` 目录是否存在
- 查看 Python 脚本输出日志

### 问题 3: Agent 分析不完整
- 确保 `.claude/agents/ccnews-analyzer.md` 存在
- 检查 daily_data.json 格式是否正确
- 重新运行 agent，并提供更明确的指令

---

## 注意事项

- ⚠️ 必须先运行 Python 脚本，再启动 Agent
- ⚠️ Python 脚本需要在虚拟环境中运行
- ⚠️ Agent 分析时会消耗少量 tokens（5-8k）
- ⚠️ 报告生成在 `cc/YYYY-MM-DD/index.md`，注意日期
- ⚠️ 每次运行会覆盖同一天的报告

---

**记住**: 新方案的核心优势是「快速」和「精准」。Python 脚本负责高效采集，Agent 负责智能分析。两者配合，5-10 分钟即可获得高质量的每日资讯。
