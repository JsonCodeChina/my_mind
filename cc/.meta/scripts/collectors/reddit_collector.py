#!/usr/bin/env python3
"""
Reddit 数据采集器

功能:
1. 从指定 subreddits 获取热门帖子
2. 抓取帖子评论
3. 智能筛选和质量评分
4. 计算热度分数

使用:
    from collectors.reddit_collector import RedditCollector
    collector = RedditCollector()
    posts = collector.fetch_all_posts()

依赖:
    pip install requests
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("错误: 缺少 requests 库")
    print("请运行: pip install requests")
    exit(1)

logger = logging.getLogger(__name__)


class RedditCollector:
    """Reddit 数据采集器（无需认证，使用公开 JSON API）"""

    # 目标 Subreddits
    SUBREDDITS = [
        'ClaudeAI',
        'ChatGPT',
        'LocalLLaMA',
        'MachineLearning',
        'artificial',
        'singularity'
    ]

    # 热度阈值
    MIN_SCORE = 50
    MAX_POSTS_PER_SUBREDDIT = 10
    MAX_COMMENTS_PER_POST = 5

    # API 配置
    BASE_URL = "https://www.reddit.com"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    REQUEST_TIMEOUT = 10

    def __init__(self):
        """初始化采集器"""
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})

    def fetch_all_posts(self, subreddits: List[str] = None) -> List[Dict]:
        """从所有 subreddits 获取热门帖子"""
        subreddits = subreddits or self.SUBREDDITS
        all_posts = []

        for subreddit in subreddits:
            logger.info(f"正在抓取 r/{subreddit}...")
            posts = self.fetch_hot_posts(subreddit)
            all_posts.extend(posts)
            logger.info(f"  ✓ 获取到 {len(posts)} 个帖子")

        # 按热度排序
        all_posts.sort(key=lambda x: x['heat_score'], reverse=True)
        logger.info(f"✓ 总共获取到 {len(all_posts)} 个 Reddit 帖子")

        return all_posts

    def fetch_hot_posts(self, subreddit: str, limit: int = None) -> List[Dict]:
        """从指定 subreddit 获取热门帖子"""
        limit = limit or self.MAX_POSTS_PER_SUBREDDIT
        url = f"{self.BASE_URL}/r/{subreddit}/hot.json"
        params = {'limit': limit * 2}  # 多抓取一些以便筛选

        try:
            response = self.session.get(url, params=params, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            posts = []
            for child in data['data']['children']:
                post_raw = child['data']

                # 跳过置顶帖
                if post_raw.get('stickied', False):
                    continue

                # 跳过低分帖子
                if post_raw.get('score', 0) < self.MIN_SCORE:
                    continue

                post_data = self._parse_post(post_raw, subreddit)
                posts.append(post_data)

            # 按热度排序并限制数量
            posts.sort(key=lambda x: x['heat_score'], reverse=True)
            return posts[:limit]

        except requests.RequestException as e:
            logger.error(f"抓取 r/{subreddit} 失败: {e}")
            return []

    def fetch_comments(self, post_id: str, subreddit: str) -> List[Dict]:
        """获取帖子评论"""
        url = f"{self.BASE_URL}/r/{subreddit}/comments/{post_id}.json"

        try:
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # Reddit API 返回 [post, comments]
            if len(data) < 2:
                return []

            comments_data = data[1]['data']['children']
            comments = []

            for child in comments_data:
                if child['kind'] != 't1':  # t1 = comment
                    continue

                comment_raw = child['data']
                comment = self._parse_comment(comment_raw)

                if comment and comment['quality_score'] > 5:
                    comments.append(comment)

            # 按质量排序
            comments.sort(key=lambda x: x['quality_score'], reverse=True)
            return comments[:self.MAX_COMMENTS_PER_POST]

        except requests.RequestException as e:
            logger.warning(f"获取评论失败 (post_id={post_id}): {e}")
            return []

    def _parse_post(self, post_raw: Dict, subreddit: str) -> Dict:
        """解析帖子数据"""
        post_id = post_raw['id']
        created_utc = datetime.fromtimestamp(post_raw['created_utc'], tz=timezone.utc)

        post_data = {
            'post_id': post_id,
            'subreddit': subreddit,
            'title': post_raw['title'],
            'selftext': post_raw.get('selftext', '')[:2000],  # 限制长度
            'author': post_raw.get('author', '[deleted]'),
            'score': post_raw.get('score', 0),
            'num_comments': post_raw.get('num_comments', 0),
            'upvote_ratio': post_raw.get('upvote_ratio', 0),
            'url': f"{self.BASE_URL}{post_raw['permalink']}",
            'created_at': created_utc.isoformat(),
            'heat_score': 0
        }

        # 计算热度分数
        post_data['heat_score'] = self.calculate_heat_score(post_data)

        return post_data

    def _parse_comment(self, comment_raw: Dict) -> Optional[Dict]:
        """解析评论数据"""
        # 跳过已删除或自动删除的评论
        body = comment_raw.get('body', '')
        if not body or body in ['[deleted]', '[removed]']:
            return None

        created_utc = datetime.fromtimestamp(comment_raw['created_utc'], tz=timezone.utc)

        comment_data = {
            'comment_id': comment_raw['id'],
            'author': comment_raw.get('author', '[deleted]'),
            'body': body[:1000],  # 限制长度
            'score': comment_raw.get('score', 0),
            'created_at': created_utc.isoformat(),
            'is_solution': False,
            'quality_score': 0
        }

        # 检测是否是解决方案
        comment_data['is_solution'] = self._detect_solution(body)

        # 计算质量分数
        comment_data['quality_score'] = self._calculate_comment_quality(comment_data)

        return comment_data

    def calculate_heat_score(self, post: Dict) -> float:
        """计算帖子热度分数"""
        score = post['score']
        num_comments = post['num_comments']
        upvote_ratio = post['upvote_ratio']

        # 基础分数
        base_score = (score * 2) + (num_comments * 3) + (upvote_ratio * 10)

        # 时间衰减（新帖子加分）
        created_at = datetime.fromisoformat(post['created_at'].replace('Z', '+00:00'))
        hours_old = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600

        time_bonus = 0
        if hours_old < 6:
            time_bonus = 30
        elif hours_old < 24:
            time_bonus = 15
        elif hours_old < 72:
            time_bonus = 5

        heat_score = base_score + time_bonus
        return round(heat_score, 2)

    def _detect_solution(self, text: str) -> bool:
        """检测是否包含解决方案"""
        solution_keywords = [
            'solution', 'fix', 'solved', 'works for me', 'workaround',
            'here\'s how', 'try this', 'you can', 'I found that'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in solution_keywords)

    def _calculate_comment_quality(self, comment: Dict) -> float:
        """计算评论质量分数"""
        score = 0

        # 点赞数权重高
        score += comment['score'] * 3

        # 长度加分
        text_length = len(comment['body'])
        if 100 < text_length < 500:
            score += 10
        elif 500 <= text_length < 1000:
            score += 5

        # 是解决方案
        if comment['is_solution']:
            score += 20

        # 包含代码块
        if '```' in comment['body'] or '`' in comment['body']:
            score += 10

        # 包含链接
        if 'http' in comment['body']:
            score += 5

        return round(score, 2)


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    collector = RedditCollector()

    # 测试单个 subreddit
    print("\n测试单个 subreddit (r/ClaudeAI):")
    posts = collector.fetch_hot_posts('ClaudeAI', limit=3)
    for post in posts:
        print(f"  {post['title'][:60]}... (热度: {post['heat_score']})")

    # 测试抓取评论
    if posts:
        print(f"\n测试抓取评论 (post_id: {posts[0]['post_id']}):")
        comments = collector.fetch_comments(posts[0]['post_id'], 'ClaudeAI')
        for comment in comments[:3]:
            print(f"  {comment['author']}: {comment['body'][:50]}... (质量: {comment['quality_score']})")

    # 测试全部 subreddits
    print("\n测试全部 subreddits:")
    all_posts = collector.fetch_all_posts()
    print(f"  ✓ 总共抓取到 {len(all_posts)} 个帖子")
    print("\n前5热门:")
    for i, post in enumerate(all_posts[:5], 1):
        print(f"  {i}. [{post['subreddit']}] {post['title'][:50]}... (热度: {post['heat_score']})")
