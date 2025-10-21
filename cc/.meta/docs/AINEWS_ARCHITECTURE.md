# AI News 多数据源架构设计

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     ainews 命令入口                          │
│              (聚合所有 AI 领域动态)                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │  Data Collectors   │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┬─────────────┐
    │              │              │              │             │
    v              v              v              v             v
┌────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│ GitHub │  │  Reddit  │  │ HN/Algolia│  │ AI News  │  │  Model   │
│ Issues │  │   API    │  │    API    │  │  Sites   │  │ Rankings │
└────────┘  └──────────┘  └───────────┘  └──────────┘  └──────────┘
    │              │              │              │             │
    └──────────────┴──────────────┴──────────────┴─────────────┘
                                  │
                          ┌───────v────────┐
                          │  Unified DB    │
                          │  (ainews.db)   │
                          └───────┬────────┘
                                  │
                          ┌───────v────────┐
                          │  AI Analyst    │
                          │  (多源分析)    │
                          └───────┬────────┘
                                  │
                          ┌───────v────────┐
                          │  Daily Report  │
                          │  (AI全景)      │
                          └────────────────┘
```

## 2. 数据源详细设计

### 2.1 GitHub Issues (已有)
- **目标**: Claude Code、Cursor、Windsurf 等 AI 编程工具
- **数据**: Issues、评论、趋势
- **更新频率**: 每天

### 2.2 Reddit (新增)
- **目标子版**:
  - r/ClaudeAI
  - r/ChatGPT
  - r/LocalLLaMA
  - r/MachineLearning
  - r/artificial
- **数据**: 热门帖子、评论、社区情绪
- **更新频率**: 每天
- **API**: Reddit API (免费，需注册应用)

### 2.3 Hacker News (已有)
- **目标关键词**: Claude, GPT, AI, LLM
- **数据**: 讨论、评论
- **更新频率**: 每天

### 2.4 AI News Sites (新增)
- **目标站点**:
  - TechCrunch AI
  - VentureBeat AI
  - The Verge AI
  - OpenAI Blog
  - Anthropic Blog
  - AI News (artificialintelligence-news.com)
- **数据**: 文章标题、摘要、链接
- **采集方式**: RSS Feed / Web Scraping
- **更新频率**: 每天

### 2.5 Model Rankings (新增)
- **目标来源**:
  - LMSYS Chatbot Arena (https://chat.lmsys.org/leaderboard)
  - HuggingFace Open LLM Leaderboard
  - Artificial Analysis (https://artificialanalysis.ai/)
- **数据**: 模型排名、ELO 分数、性能指标
- **更新频率**: 每周
- **采集方式**: API / Web Scraping

### 2.6 Twitter/X (可选)
- **目标账号**:
  - @AnthropicAI
  - @OpenAI
  - @GoogleAI
  - AI 领域 KOL
- **挑战**: 需要 API (付费)
- **优先级**: P2 (暂缓)

## 3. 数据库 Schema 扩展

### 3.1 新增表结构

```sql
-- Reddit 帖子表
CREATE TABLE reddit_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT UNIQUE NOT NULL,
    subreddit TEXT NOT NULL,
    title TEXT NOT NULL,
    selftext TEXT,
    author TEXT,
    score INTEGER DEFAULT 0,
    num_comments INTEGER DEFAULT 0,
    upvote_ratio REAL DEFAULT 0,
    heat_score REAL DEFAULT 0,
    url TEXT,
    created_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reddit 评论表
CREATE TABLE reddit_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    comment_id TEXT UNIQUE NOT NULL,
    author TEXT,
    body TEXT,
    score INTEGER DEFAULT 0,
    quality_score REAL DEFAULT 0,
    is_solution BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES reddit_posts(post_id)
);

-- AI 新闻文章表
CREATE TABLE ai_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,  -- 'techcrunch', 'verge', 'openai-blog'
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,
    heat_score REAL DEFAULT 0,
    category TEXT,  -- 'product', 'research', 'business', 'ethics'
    tags TEXT,  -- JSON array
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型排名表 (已有，增强)
ALTER TABLE model_rankings ADD COLUMN speed_tokens_per_sec REAL;
ALTER TABLE model_rankings ADD COLUMN cost_per_1m_tokens REAL;
ALTER TABLE model_rankings ADD COLUMN context_window INTEGER;
ALTER TABLE model_rankings ADD COLUMN quality_index REAL;

-- 产品更新表 (追踪多个产品)
CREATE TABLE product_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,  -- 'claude-code', 'cursor', 'windsurf', 'openai'
    update_type TEXT,  -- 'version', 'feature', 'pricing', 'outage'
    title TEXT NOT NULL,
    description TEXT,
    version TEXT,
    url TEXT,
    impact_score REAL DEFAULT 0,  -- 影响力评分
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 索引优化

```sql
CREATE INDEX idx_reddit_subreddit ON reddit_posts(subreddit);
CREATE INDEX idx_reddit_score ON reddit_posts(score DESC);
CREATE INDEX idx_news_source ON ai_news(source);
CREATE INDEX idx_news_category ON ai_news(category);
CREATE INDEX idx_model_rank ON model_rankings(rank);
CREATE INDEX idx_product ON product_updates(product);
```

## 4. 数据采集器实现

### 4.1 Reddit Collector

```python
class RedditCollector:
    """Reddit 数据采集器"""

    SUBREDDITS = ['ClaudeAI', 'ChatGPT', 'LocalLLaMA', 'MachineLearning']

    def fetch_hot_posts(self, subreddit: str, limit: int = 10) -> List[Dict]:
        """获取热门帖子"""
        pass

    def fetch_comments(self, post_id: str) -> List[Dict]:
        """获取评论"""
        pass

    def calculate_heat_score(self, post: Dict) -> float:
        """计算热度分数"""
        # score * 2 + num_comments * 3 + upvote_ratio * 10
        pass
```

### 4.2 AI News Collector

```python
class AINewsCollector:
    """AI 新闻采集器"""

    SOURCES = {
        'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'verge': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
        'openai': 'https://openai.com/blog/rss',
        'anthropic': 'https://www.anthropic.com/news/rss'
    }

    def fetch_rss_feed(self, source: str) -> List[Dict]:
        """从 RSS 获取文章"""
        pass

    def extract_summary(self, content: str) -> str:
        """提取摘要（前300字或AI总结）"""
        pass

    def categorize_article(self, title: str, content: str) -> str:
        """分类文章（product/research/business/ethics）"""
        pass
```

### 4.3 Model Rankings Collector

```python
class ModelRankingsCollector:
    """模型排名采集器"""

    SOURCES = {
        'lmsys': 'https://chat.lmsys.org/api/leaderboard',
        'huggingface': 'https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard'
    }

    def fetch_lmsys_rankings(self) -> List[Dict]:
        """获取 LMSYS 排名"""
        pass

    def fetch_huggingface_rankings(self) -> List[Dict]:
        """获取 HuggingFace 排名"""
        pass

    def calculate_quality_index(self, model: Dict) -> float:
        """计算综合质量指数"""
        # (ELO + speed_score + cost_score) / 3
        pass
```

## 5. 命令接口设计

### 5.1 ainews 命令

```bash
# 完整 AI 动态报告（默认）
/ainews

# 只看特定数据源
/ainews --sources reddit,hn

# 只看特定主题
/ainews --topics "Claude Code,GPT-4,Cursor"

# 自定义时间范围
/ainews --days 7

# 快速模式（减少评论抓取）
/ainews --quick
```

### 5.2 配置文件

```json
// .claude/config/ainews.json
{
  "sources": {
    "github": {
      "enabled": true,
      "repos": [
        "anthropics/claude-code",
        "getcursor/cursor",
        "codeiumai/windsurf"
      ]
    },
    "reddit": {
      "enabled": true,
      "subreddits": ["ClaudeAI", "ChatGPT", "LocalLLaMA", "MachineLearning", "artificial"],
      "min_score": 50
    },
    "hn": {
      "enabled": true,
      "keywords": ["Claude", "GPT", "AI", "LLM", "Anthropic"]
    },
    "news": {
      "enabled": true,
      "sites": ["techcrunch", "verge", "openai", "anthropic"]
    },
    "models": {
      "enabled": true,
      "leaderboards": ["lmsys", "huggingface", "artificial_analysis"]
    }
  },
  "report": {
    "target_length": 150,
    "include_comments": true,
    "max_comments_per_item": 5,
    "sections": [
      "headlines",
      "hot_discussions",
      "model_updates",
      "product_news",
      "community_pulse"
    ]
  }
}
```

## 6. AI Analyst Agent 升级

### 6.1 新增分析能力

```markdown
## ainews-analyst 职责

1. **跨源整合**: 识别同一话题在不同平台的讨论
2. **趋势识别**: 发现新兴话题和衰退话题
3. **情绪对比**: GitHub (技术) vs Reddit (用户) vs HN (行业)
4. **模型追踪**: 排名变化、新模型发布、性能对比
5. **产品动态**: 多个产品的版本更新、功能对比
6. **影响预测**: 某个事件对行业/用户的影响

输出报告结构:
- 📰 AI 行业头条 (3-5条)
- 🔥 社区热议话题 (5-8个)
- 🤖 模型动态 (排名变化、新模型)
- 📦 产品更新 (Claude/Cursor/Windsurf/OpenAI)
- 💬 社区脉搏 (情绪分析)
- 🔮 趋势预测
```

## 7. 实施优先级

### P0 (立即实施)
1. 扩展数据库 schema
2. 实现 Reddit 采集器
3. 实现 AI News 采集器
4. 创建 ainews 命令
5. 升级 AI Analyst

### P1 (本周完成)
1. 实现 Model Rankings 采集器
2. 添加多产品支持 (Cursor, Windsurf)
3. 完善配置系统

### P2 (未来优化)
1. Twitter/X 集成 (需要 API 费用评估)
2. 可视化仪表板
3. 邮件订阅功能
4. Telegram/Discord bot

## 8. 性能目标

- **数据采集**: < 40秒 (多源并发)
- **AI 分析**: < 20秒
- **总耗时**: < 60秒
- **Token 消耗**: 12-18K
- **报告长度**: 150行 (±20)
- **数据覆盖**: 5个数据源，50+ 数据点

## 9. 示例报告结构

```markdown
# AI 动态日报 | 2025-10-17

## 📰 行业头条

1. Anthropic 发布 Claude 3.5 Sonnet (New) - OpenAI Blog
2. LMSYS Arena: GPT-4o 重回第一 - LMSYS Leaderboard
3. Cursor 融资 6000 万美元 B 轮 - TechCrunch

## 🔥 社区热议

### Claude Code 主题自动切换 (热度: 234)
- **GitHub**: Issue #2990 (91.0) - 11 评论
- **Reddit**: r/ClaudeAI - "Dark mode is broken" (156 upvotes)
- **HN**: 无相关讨论

社区情绪: 😐 期待改进
关键评论: @antonioacg "成为主要问题..."

...
```

## 10. 技术栈

- **Python 3.9+**
- **SQLite** (数据存储)
- **Requests** (HTTP)
- **BeautifulSoup4** (HTML 解析)
- **PRAW** (Reddit API)
- **feedparser** (RSS 解析)
- **pandas** (数据处理，可选)
