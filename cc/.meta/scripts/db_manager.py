#!/usr/bin/env python3
"""
SQLite 数据库管理器

功能：
1. 初始化数据库表结构
2. 数据插入、查询、更新
3. 趋势分析和历史对比
4. 数据清理和维护

使用：
    from db_manager import DatabaseManager
    db = DatabaseManager("ccnews.db")
    db.insert_issue(issue_data)
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite 数据库管理器"""

    def __init__(self, db_path: str = "/Users/shenbo/Desktop/mind/cc/ccnews.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        """初始化所有表结构"""

        # Issues 表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            state TEXT,
            comments INTEGER DEFAULT 0,
            reactions INTEGER DEFAULT 0,
            heat_score REAL DEFAULT 0,
            labels TEXT,  -- JSON 数组
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'claude-code'
        )
        """)

        # 评论表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_number INTEGER NOT NULL,
            author TEXT,
            body TEXT,
            upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            is_solution BOOLEAN DEFAULT 0,
            is_interesting BOOLEAN DEFAULT 0,
            quality_score REAL DEFAULT 0,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_number) REFERENCES issues(issue_number)
        )
        """)

        # HN 讨论表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS hn_discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objectID TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            hn_url TEXT,
            points INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            heat_score REAL DEFAULT 0,
            author TEXT,
            created_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # HN 评论表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS hn_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id TEXT NOT NULL,
            author TEXT,
            text TEXT,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            quality_score REAL DEFAULT 0,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discussion_id) REFERENCES hn_discussions(objectID)
        )
        """)

        # 模型排名表（为未来准备）
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            rank INTEGER,
            elo_score REAL,
            source TEXT,  -- 'lmsys', 'huggingface'
            category TEXT,  -- 'overall', 'coding', 'reasoning'
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 版本历史表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS version_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,  -- 'claude-code', 'cursor', 'openai'
            version TEXT NOT NULL,
            release_date DATE,
            changelog TEXT,
            is_major BOOLEAN DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Reddit 帖子表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
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
        )
        """)

        # Reddit 评论表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_comments (
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
        )
        """)

        # AI 新闻文章表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            url TEXT NOT NULL,
            author TEXT,
            published_at TIMESTAMP,
            heat_score REAL DEFAULT 0,
            category TEXT,
            tags TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 产品更新表
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            update_type TEXT,
            title TEXT NOT NULL,
            description TEXT,
            version TEXT,
            url TEXT,
            impact_score REAL DEFAULT 0,
            published_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建索引
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_issue_number ON issues(issue_number)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_issue_fetched ON issues(fetched_at)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_comment_issue ON issue_comments(issue_number)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reddit_subreddit ON reddit_posts(subreddit)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reddit_score ON reddit_posts(score DESC)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_news_source ON ai_news(source)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_news_category ON ai_news(category)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_product ON product_updates(product)"
        )

        self.conn.commit()
        logger.info(f"数据库表初始化完成: {self.db_path}")

    # ========================================================================
    # Issues 相关操作
    # ========================================================================

    def insert_issue(self, issue_data: Dict) -> int:
        """插入或更新 Issue 数据"""
        try:
            self.cursor.execute("""
            INSERT INTO issues (
                issue_number, title, url, state, comments, reactions,
                heat_score, labels, created_at, updated_at, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_data['number'],
                issue_data['title'],
                issue_data['url'],
                issue_data['state'],
                issue_data['comments'],
                issue_data['reactions']['total_count'],
                issue_data['heat_score'],
                json.dumps([l['name'] for l in issue_data.get('labels', [])]),
                issue_data['created_at'],
                issue_data['updated_at'],
                issue_data.get('source', 'claude-code')
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError as e:
            logger.warning(f"Issue {issue_data['number']} 可能重复插入: {e}")
            return -1

    def insert_comment(self, issue_number: int, comment_data: Dict) -> int:
        """插入评论数据"""
        try:
            self.cursor.execute("""
            INSERT INTO issue_comments (
                issue_number, author, body, upvotes, created_at,
                is_solution, is_interesting, quality_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_number,
                comment_data['author'],
                comment_data['body'],
                comment_data['upvotes'],
                comment_data.get('created_at'),
                comment_data.get('is_solution', False),
                comment_data.get('is_interesting', False),
                comment_data.get('quality_score', 0)
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入评论失败: {e}")
            return -1

    def get_issue_trend(self, issue_number: int, days: int = 7) -> Dict:
        """获取 Issue 的趋势数据"""
        since_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        self.cursor.execute("""
        SELECT heat_score, comments, reactions, fetched_at
        FROM issues
        WHERE issue_number = ?
        AND fetched_at > ?
        ORDER BY fetched_at
        """, (issue_number, since_date))

        history = [dict(row) for row in self.cursor.fetchall()]

        if len(history) < 2:
            return {
                "trend": "new",
                "heat_change": 0,
                "heat_pct": 0,
                "comment_rate": 0,
                "data_points": len(history)
            }

        latest = history[-1]
        oldest = history[0]

        heat_change = latest['heat_score'] - oldest['heat_score']
        heat_pct = (heat_change / oldest['heat_score']) * 100 if oldest['heat_score'] > 0 else 0

        comment_change = latest['comments'] - oldest['comments']
        comment_rate = comment_change / days  # 日均增速

        return {
            "trend": "rising" if heat_change > 0 else "falling",
            "heat_change": round(heat_change, 1),
            "heat_pct": round(heat_pct, 1),
            "comment_rate": round(comment_rate, 1),
            "data_points": len(history),
            "oldest_score": oldest['heat_score'],
            "latest_score": latest['heat_score']
        }

    def get_top_comments(self, issue_number: int, limit: int = 5) -> List[Dict]:
        """获取 Issue 的高赞评论"""
        self.cursor.execute("""
        SELECT author, body, upvotes, is_solution, is_interesting, quality_score
        FROM issue_comments
        WHERE issue_number = ?
        ORDER BY quality_score DESC, upvotes DESC
        LIMIT ?
        """, (issue_number, limit))

        return [dict(row) for row in self.cursor.fetchall()]

    # ========================================================================
    # HN 讨论相关操作
    # ========================================================================

    def insert_discussion(self, discussion_data: Dict) -> int:
        """插入 HN 讨论"""
        try:
            self.cursor.execute("""
            INSERT OR REPLACE INTO hn_discussions (
                objectID, title, url, hn_url, points, comments,
                heat_score, author, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                discussion_data['objectID'],
                discussion_data['title'],
                discussion_data.get('url', ''),
                discussion_data['hn_url'],
                discussion_data['points'],
                discussion_data['comments'],
                discussion_data['heat_score'],
                discussion_data.get('author', ''),
                discussion_data.get('created_at', '')
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入 HN 讨论失败: {e}")
            return -1

    def insert_hn_comment(self, discussion_id: str, comment_data: Dict) -> int:
        """插入 HN 评论"""
        try:
            self.cursor.execute("""
            INSERT INTO hn_comments (
                discussion_id, author, text, points, created_at, quality_score
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                discussion_id,
                comment_data['author'],
                comment_data['text'],
                comment_data.get('points', 0),
                comment_data.get('created_at', ''),
                comment_data.get('quality_score', 0)
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入 HN 评论失败: {e}")
            return -1

    # ========================================================================
    # 版本相关操作
    # ========================================================================

    def insert_version(self, product: str, version: str, release_date: str = None,
                      changelog: str = "", is_major: bool = False) -> int:
        """插入版本记录"""
        try:
            self.cursor.execute("""
            INSERT INTO version_history (
                product, version, release_date, changelog, is_major
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                product,
                version,
                release_date or datetime.now().strftime('%Y-%m-%d'),
                changelog,
                is_major
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入版本失败: {e}")
            return -1

    def get_latest_version(self, product: str) -> Optional[Dict]:
        """获取最新版本"""
        self.cursor.execute("""
        SELECT version, release_date, changelog
        FROM version_history
        WHERE product = ?
        ORDER BY recorded_at DESC
        LIMIT 1
        """, (product,))

        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ========================================================================
    # 数据清理
    # ========================================================================

    def cleanup_old_data(self, days: int = 30):
        """清理超过 N 天的旧数据"""
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # 删除旧 Issues
        self.cursor.execute("""
        DELETE FROM issues WHERE fetched_at < ?
        """, (cutoff_date,))

        # 删除旧评论
        self.cursor.execute("""
        DELETE FROM issue_comments WHERE fetched_at < ?
        """, (cutoff_date,))

        # 删除旧 HN 讨论
        self.cursor.execute("""
        DELETE FROM hn_discussions WHERE fetched_at < ?
        """, (cutoff_date,))

        # 删除旧 Reddit 帖子
        self.cursor.execute("""
        DELETE FROM reddit_posts WHERE fetched_at < ?
        """, (cutoff_date,))

        # 删除旧 AI 新闻
        self.cursor.execute("""
        DELETE FROM ai_news WHERE fetched_at < ?
        """, (cutoff_date,))

        self.conn.commit()
        logger.info(f"已清理 {days} 天前的旧数据")

    # ========================================================================
    # Reddit 相关操作
    # ========================================================================

    def insert_reddit_post(self, post_data: Dict) -> int:
        """插入 Reddit 帖子"""
        try:
            self.cursor.execute("""
            INSERT OR REPLACE INTO reddit_posts (
                post_id, subreddit, title, selftext, author, score,
                num_comments, upvote_ratio, heat_score, url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data['post_id'],
                post_data['subreddit'],
                post_data['title'],
                post_data.get('selftext', ''),
                post_data.get('author', ''),
                post_data['score'],
                post_data['num_comments'],
                post_data.get('upvote_ratio', 0),
                post_data['heat_score'],
                post_data.get('url', ''),
                post_data.get('created_at', '')
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入 Reddit 帖子失败: {e}")
            return -1

    def insert_reddit_comment(self, post_id: str, comment_data: Dict) -> int:
        """插入 Reddit 评论"""
        try:
            self.cursor.execute("""
            INSERT OR REPLACE INTO reddit_comments (
                post_id, comment_id, author, body, score,
                quality_score, is_solution, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id,
                comment_data['comment_id'],
                comment_data.get('author', ''),
                comment_data['body'],
                comment_data.get('score', 0),
                comment_data.get('quality_score', 0),
                comment_data.get('is_solution', False),
                comment_data.get('created_at', '')
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入 Reddit 评论失败: {e}")
            return -1

    def get_reddit_top_posts(self, subreddit: str = None, limit: int = 10) -> List[Dict]:
        """获取热门 Reddit 帖子"""
        if subreddit:
            self.cursor.execute("""
            SELECT * FROM reddit_posts
            WHERE subreddit = ?
            ORDER BY heat_score DESC
            LIMIT ?
            """, (subreddit, limit))
        else:
            self.cursor.execute("""
            SELECT * FROM reddit_posts
            ORDER BY heat_score DESC
            LIMIT ?
            """, (limit,))

        return [dict(row) for row in self.cursor.fetchall()]

    # ========================================================================
    # AI News 相关操作
    # ========================================================================

    def insert_ai_news(self, news_data: Dict) -> int:
        """插入 AI 新闻"""
        try:
            self.cursor.execute("""
            INSERT OR REPLACE INTO ai_news (
                article_id, source, title, summary, content, url,
                author, published_at, heat_score, category, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news_data['article_id'],
                news_data['source'],
                news_data['title'],
                news_data.get('summary', ''),
                news_data.get('content', ''),
                news_data['url'],
                news_data.get('author', ''),
                news_data.get('published_at', ''),
                news_data.get('heat_score', 0),
                news_data.get('category', ''),
                json.dumps(news_data.get('tags', []))
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入 AI 新闻失败: {e}")
            return -1

    def get_recent_ai_news(self, source: str = None, limit: int = 10) -> List[Dict]:
        """获取最新 AI 新闻"""
        if source:
            self.cursor.execute("""
            SELECT * FROM ai_news
            WHERE source = ?
            ORDER BY published_at DESC
            LIMIT ?
            """, (source, limit))
        else:
            self.cursor.execute("""
            SELECT * FROM ai_news
            ORDER BY published_at DESC
            LIMIT ?
            """, (limit,))

        return [dict(row) for row in self.cursor.fetchall()]

    # ========================================================================
    # Product Updates 相关操作
    # ========================================================================

    def insert_product_update(self, update_data: Dict) -> int:
        """插入产品更新"""
        try:
            self.cursor.execute("""
            INSERT INTO product_updates (
                product, update_type, title, description, version,
                url, impact_score, published_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                update_data['product'],
                update_data.get('update_type', ''),
                update_data['title'],
                update_data.get('description', ''),
                update_data.get('version', ''),
                update_data.get('url', ''),
                update_data.get('impact_score', 0),
                update_data.get('published_at', '')
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception as e:
            logger.error(f"插入产品更新失败: {e}")
            return -1

    def get_product_updates(self, product: str = None, limit: int = 10) -> List[Dict]:
        """获取产品更新记录"""
        if product:
            self.cursor.execute("""
            SELECT * FROM product_updates
            WHERE product = ?
            ORDER BY published_at DESC
            LIMIT ?
            """, (product, limit))
        else:
            self.cursor.execute("""
            SELECT * FROM product_updates
            ORDER BY published_at DESC
            LIMIT ?
            """, (limit,))

        return [dict(row) for row in self.cursor.fetchall()]

    def __del__(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()


# ============================================================================
# 工具函数
# ============================================================================

def predict_resolution_time(comment_rate: float, heat_score: float, state: str) -> str:
    """预测问题修复时间"""
    if state == "closed":
        return "已解决"

    # 基于评论增速和热度判断优先级
    if heat_score > 500 or comment_rate > 10:
        return "🔥 超高优先级，预计 1-3 天内官方回应"
    elif heat_score > 200 or comment_rate > 5:
        return "⚠️ 高优先级，预计 3-7 天内处理"
    elif heat_score > 100 or comment_rate > 2:
        return "📌 中优先级，预计 1-2 周内关注"
    else:
        return "💤 低优先级，可能需要较长时间"


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    db = DatabaseManager()
    print("✅ 数据库初始化成功！")

    # 测试插入数据
    test_issue = {
        'number': 9999,
        'title': '测试 Issue',
        'url': 'https://github.com/test',
        'state': 'open',
        'comments': 10,
        'reactions': {'total_count': 5},
        'heat_score': 25.5,
        'labels': [{'name': 'bug'}],
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }

    issue_id = db.insert_issue(test_issue)
    print(f"✅ 测试 Issue 插入成功，ID: {issue_id}")
