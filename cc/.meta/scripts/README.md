# Claude Code 数据采集脚本

自动化采集 Claude Code 相关数据的 Python 脚本。

## 功能特性

- ✅ **GitHub Issues**: 自动获取最近的热门 Issues，按热度评分排序
- ✅ **HN 讨论**: 从 Hacker News 获取相关讨论
- ✅ **社区文章**: 从 cc.deeptoai.com 获取最新文章
- ✅ **版本检测**: 自动检测 Claude Code 最新版本
- ✅ **智能筛选**: 基于热度算法自动过滤低价值内容
- ✅ **高性能**: 5-10 秒完成数据采集
- ✅ **错误处理**: 完善的重试和降级机制

## 安装

### 1. 创建虚拟环境

```bash
cd /Users/shenbo/Desktop/mind/cc
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install requests beautifulsoup4 python-dateutil
```

## 使用方法

### 基本用法

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行脚本（使用默认设置）
python scripts/fetch_data.py
```

### 自定义参数

```bash
# 指定输出路径
python scripts/fetch_data.py --output /path/to/output.json

# 调整回溯天数
python scripts/fetch_data.py --github-days 7 --hn-days 14

# 显示详细日志
python scripts/fetch_data.py --verbose
```

### 参数说明

| 参数 | 短参数 | 说明 | 默认值 |
|------|--------|------|--------|
| `--output` | `-o` | 输出文件路径 | `cc/cache/daily_data.json` |
| `--github-days` | - | GitHub Issues 回溯天数 | 3 |
| `--hn-days` | - | HN 讨论回溯天数 | 7 |
| `--verbose` | `-v` | 显示详细日志 | False |

## 输出数据格式

脚本生成的 JSON 文件包含以下结构：

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

详细的数据结构定义见 `cc/schemas/daily_data.schema.json`

## 热度评分算法

### GitHub Issues

```
heat_score = (评论数 × 2) + (反应数 × 1.5) + 时间加成 + 标签加成
```

- 时间加成：24小时内 +20，72小时内 +10
- 标签加成：bug +5，feature +3，priority-high +10

### HN 讨论

```
heat_score = (分数 × 1.5) + (评论数 × 2) + 时间加成 + 相关性加成
```

- 时间加成：1天内 +30，3天内 +15，7天内 +5
- 相关性加成：tutorial/guide +10，case study/production +15

### 文章质量

```
quality_score = 新鲜度(40) + 分类(30) + 关键词(20) + 长度(10)
```

详细算法文档见 `cc/docs/heat-algorithm.md`

## 筛选规则

| 类型 | 筛选标准 | 最大数量 |
|------|----------|----------|
| GitHub Issues | heat_score ≥ 20 | 5 个 |
| HN 讨论 | heat_score ≥ 50 | 3 个 |
| 社区文章 | quality_score ≥ 70 | 2 篇 |

## 性能指标

- **执行时间**: 5-10 秒
- **API 调用**: 4-6 次
- **成功率**: > 95%

## 故障排除

### 问题：requests 模块未找到

```bash
# 确保虚拟环境已激活
source venv/bin/activate
pip install requests beautifulsoup4 python-dateutil
```

### 问题：GitHub API rate limit

未认证的 GitHub API 限制为 60 次/小时，足够日常使用。如需更高限制，可以：

1. 创建 GitHub Personal Access Token
2. 在脚本中添加认证头：`headers={'Authorization': 'token YOUR_TOKEN'}`

### 问题：文章数量为 0

这是正常的！脚本使用严格的质量评分（≥70分）筛选文章。如果没有符合标准的文章，输出为空是预期行为。

可以通过以下方式调整：

```python
# 在 fetch_data.py 中修改
Config.ARTICLE_QUALITY_THRESHOLD = 50  # 降低阈值
```

### 问题：网络请求超时

脚本内置了重试机制（最多3次）。如果网络不稳定：

```python
# 在 fetch_data.py 中修改
Config.REQUEST_TIMEOUT = 30  # 增加超时时间（秒）
```

## 定时任务（可选）

使用 cron 定时运行脚本：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 9 点运行）
0 9 * * * cd /Users/shenbo/Desktop/mind/cc && source venv/bin/activate && python scripts/fetch_data.py
```

## 开发说明

### 目录结构

```
cc/
├── scripts/
│   ├── fetch_data.py           # 主脚本
│   └── README.md               # 本文档
├── cache/
│   └── daily_data.json         # 输出数据
├── schemas/
│   ├── daily_data.schema.json  # 数据结构定义
│   └── daily_data.example.json # 示例数据
├── docs/
│   └── heat-algorithm.md       # 算法文档
└── venv/                       # 虚拟环境
```

### 修改配置

在 `fetch_data.py` 的 `Config` 类中修改默认值：

```python
class Config:
    # 修改阈值
    ISSUE_HEAT_THRESHOLD = 15  # 默认 20
    HN_HEAT_THRESHOLD = 40     # 默认 50

    # 修改数量限制
    MAX_ISSUES = 10            # 默认 5
    MAX_DISCUSSIONS = 5        # 默认 3
```

### 扩展数据源

要添加新的数据源，参考现有的 `fetch_xxx()` 函数：

```python
def fetch_new_source() -> List[Dict]:
    """获取新数据源"""
    # 1. 发送请求
    # 2. 解析数据
    # 3. 计算评分
    # 4. 筛选和排序
    return results
```

## 版本历史

- **v1.0** (2025-10-14)
  - 初始版本
  - 支持 GitHub Issues、HN 讨论、社区文章、版本检测
  - 实现热度评分算法
  - 完善错误处理机制

## 许可证

本脚本是 ccnews 优化项目的一部分，供个人使用。

## 支持

如有问题，请参考：
- 技术可行性报告：`cc/research/api-feasibility.md`
- 热度算法文档：`cc/docs/heat-algorithm.md`
- 数据结构定义：`cc/schemas/daily_data.schema.json`
