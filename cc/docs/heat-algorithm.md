# 热度评分算法

## 概述
本文档定义了 ccnews 系统中用于计算内容热度和质量的评分算法。

## 1. GitHub Issues 热度评分

### 公式
```
heat_score = (comments × 2) + (reactions × 1.5) + time_bonus + label_bonus
```

### 参数说明

**基础分数：**
- `comments`: 评论数（权重 2.0）
  - 评论数反映了社区讨论的活跃度
  - 高权重因为有深度讨论的 Issue 更有价值

- `reactions`: 反应总数（权重 1.5）
  - 包括 👍 +1, 👎 -1, 😄 laugh, 🎉 hooray, 😕 confused, ❤️ heart, 🚀 rocket, 👀 eyes
  - 快速表达关注度的方式

**时间加成：**
```python
if hours_since_created < 24:
    time_bonus = 20
elif hours_since_created < 72:
    time_bonus = 10
else:
    time_bonus = 0
```

**标签加成：**
```python
priority_labels = {
    'bug': 5,
    'feature': 3,
    'has repro': 5,
    'priority-high': 10,
    'priority-critical': 15
}
```

### 阈值设置
- **高热度**: heat_score >= 50
- **中热度**: heat_score >= 20
- **低热度**: heat_score < 20

**TOP 5 筛选标准:**
只选择 heat_score >= 20 的 Issues

---

## 2. Hacker News 讨论热度评分

### 公式
```
heat_score = (points × 1.5) + (comments × 2) + time_bonus + relevance_bonus
```

### 参数说明

**基础分数：**
- `points`: HN 分数/赞数（权重 1.5）
- `comments`: 评论数（权重 2.0）

**时间加成：**
```python
if days_since_created < 1:
    time_bonus = 30
elif days_since_created < 3:
    time_bonus = 15
elif days_since_created < 7:
    time_bonus = 5
else:
    time_bonus = 0
```

**相关性加成：**
```python
# 标题或内容包含关键词
relevance_keywords = {
    'tutorial': 10,
    'guide': 10,
    'case study': 15,
    'production': 15,
    'real-world': 15,
    'comparison': 8,
    'review': 8
}
```

### 阈值设置
- **高价值**: heat_score >= 100
- **中价值**: heat_score >= 50
- **低价值**: heat_score < 50

**TOP 3 筛选标准:**
只选择 heat_score >= 50 的讨论

---

## 3. 文章质量评分

### 公式
```
quality_score = recency_score + category_score + keyword_score + length_score
```

### 参数说明

**新鲜度分数（最高 40 分）：**
```python
days_old = (today - published_date).days

if days_old < 7:
    recency_score = 40
elif days_old < 30:
    recency_score = 30
elif days_old < 90:
    recency_score = 20
else:
    recency_score = 10
```

**分类分数（最高 30 分）：**
```python
category_scores = {
    'best-practices': 30,
    'advanced-techniques': 25,
    'community-tips': 20,
    'tools': 15
}
```

**关键词分数（最高 20 分）：**
```python
high_quality_keywords = {
    '全面': 5,
    '实战': 5,
    '手把手': 5,
    '深入': 5,
    '系统': 4,
    '完整': 4,
    '详解': 4,
    'comprehensive': 5,
    'in-depth': 5,
    'complete guide': 5,
    'tutorial': 4
}
```

**内容长度分数（最高 10 分）：**
```python
if content_length > 5000:
    length_score = 10
elif content_length > 3000:
    length_score = 7
elif content_length > 1000:
    length_score = 5
else:
    length_score = 2
```

### 阈值设置
- **优质文章**: quality_score >= 70
- **良好文章**: quality_score >= 50
- **一般文章**: quality_score < 50

**推荐标准:**
- 选择 quality_score >= 70 的文章
- 最多推荐 2 篇
- 优先选择最新的文章

---

## 4. 版本更新检测

### 检测逻辑
```python
# 从 claudelog.com 提取版本号
current_version = extract_version_from_changelog()

# 对比 baseline.json
previous_version = read_baseline()['claudeCodeVersion']

is_new = current_version != previous_version
```

### 变更提取
如果是新版本，提取以下信息：
1. 版本号（如 v2.0.15）
2. 发布日期
3. 主要改进（Highlights）
4. 修复的问题（Bug fixes）
5. 新增功能（New features）

---

## 5. 算法调优建议

### 定期审查
每月审查评分算法的效果：
1. 查看被选中的内容是否真正有价值
2. 是否有高价值内容被遗漏
3. 权重是否需要调整

### 用户反馈
收集用户反馈：
- 哪些推荐的内容有用？
- 哪些推荐不太相关？
- 是否需要调整筛选数量（TOP 5, TOP 3）？

### A/B 测试
可以尝试不同的权重配置：
- 方案 A: 当前配置
- 方案 B: 提高时间权重（更关注新内容）
- 方案 C: 提高互动权重（更关注讨论热度）

---

## 附录：Python 示例实现

```python
from datetime import datetime, timezone

def calculate_issue_heat_score(issue_data):
    """计算 GitHub Issue 热度分数"""
    comments = issue_data['comments']
    reactions = issue_data['reactions']['total_count']

    # 基础分数
    base_score = (comments * 2) + (reactions * 1.5)

    # 时间加成
    created_at = datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00'))
    hours_old = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600

    if hours_old < 24:
        time_bonus = 20
    elif hours_old < 72:
        time_bonus = 10
    else:
        time_bonus = 0

    # 标签加成
    label_bonus = 0
    priority_labels = {
        'bug': 5,
        'feature': 3,
        'has repro': 5,
        'priority-high': 10,
        'priority-critical': 15
    }

    for label in issue_data['labels']:
        label_name = label['name']
        if label_name in priority_labels:
            label_bonus += priority_labels[label_name]

    heat_score = base_score + time_bonus + label_bonus
    return heat_score

def calculate_hn_heat_score(story_data):
    """计算 HN 讨论热度分数"""
    points = story_data['points']
    comments = story_data['num_comments']

    # 基础分数
    base_score = (points * 1.5) + (comments * 2)

    # 时间加成
    created_timestamp = story_data['created_at_i']
    days_old = (datetime.now(timezone.utc).timestamp() - created_timestamp) / 86400

    if days_old < 1:
        time_bonus = 30
    elif days_old < 3:
        time_bonus = 15
    elif days_old < 7:
        time_bonus = 5
    else:
        time_bonus = 0

    # 相关性加成
    relevance_bonus = 0
    title_lower = story_data['title'].lower()
    relevance_keywords = {
        'tutorial': 10,
        'guide': 10,
        'case study': 15,
        'production': 15,
        'real-world': 15
    }

    for keyword, bonus in relevance_keywords.items():
        if keyword in title_lower:
            relevance_bonus += bonus

    heat_score = base_score + time_bonus + relevance_bonus
    return heat_score

def calculate_article_quality_score(article_data):
    """计算文章质量分数"""
    # 新鲜度分数
    if 'published_at' in article_data:
        published_date = datetime.fromisoformat(article_data['published_at'])
        days_old = (datetime.now() - published_date).days

        if days_old < 7:
            recency_score = 40
        elif days_old < 30:
            recency_score = 30
        elif days_old < 90:
            recency_score = 20
        else:
            recency_score = 10
    else:
        recency_score = 10

    # 分类分数
    category_scores = {
        'best-practices': 30,
        'advanced-techniques': 25,
        'community-tips': 20,
        'tools': 15
    }
    category_score = category_scores.get(article_data['category'], 10)

    # 关键词分数
    keyword_score = 0
    title = article_data['title']
    high_quality_keywords = {
        '全面': 5, '实战': 5, '手把手': 5, '深入': 5,
        'comprehensive': 5, 'in-depth': 5, 'complete guide': 5
    }

    for keyword, score in high_quality_keywords.items():
        if keyword in title:
            keyword_score += score

    keyword_score = min(keyword_score, 20)  # 最高 20 分

    # 内容长度分数（需要爬取内容）
    length_score = 5  # 默认值

    quality_score = recency_score + category_score + keyword_score + length_score
    return quality_score
```

---

**文档版本**: 1.0
**最后更新**: 2025-10-14
**作者**: ccnews 优化项目
