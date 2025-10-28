#!/usr/bin/env python3
"""
共享数据采集工具模块

提供可复用的函数：
- HTTP 请求
- 热度评分算法
- 评论抓取和筛选
"""

import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dateutil import parser as date_parser


logger = logging.getLogger(__name__)


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    # API URLs
    GITHUB_API_BASE = "https://api.github.com"
    HN_ALGOLIA_API = "https://hn.algolia.com/api/v1/search"
    HN_ITEM_API = "https://hacker-news.firebaseio.com/v0/item"

    # 请求超时
    REQUEST_TIMEOUT = 10

    # User-Agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


# ============================================================================
# 工具函数
# ============================================================================

def make_request(url: str, params: Optional[Dict] = None,
                 headers: Optional[Dict] = None) -> Optional[requests.Response]:
    """发送 HTTP 请求，带重试机制"""
    default_headers = {"User-Agent": Config.USER_AGENT}
    if headers:
        default_headers.update(headers)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params=params,
                headers=default_headers,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"请求最终失败: {url}")
                return None

    return None


def parse_date(date_string: str) -> Optional[datetime]:
    """解析日期字符串"""
    try:
        return date_parser.parse(date_string)
    except Exception:
        return None


# ============================================================================
# 热度评分算法
# ============================================================================

def calculate_issue_heat_score(issue_data: Dict) -> float:
    """计算 GitHub Issue 热度分数"""
    comments = issue_data.get('comments', 0)
    reactions = issue_data.get('reactions', {}).get('total_count', 0)

    # 基础分数
    base_score = (comments * 2) + (reactions * 1.5)

    # 时间加成
    created_at = parse_date(issue_data.get('created_at', ''))
    time_bonus = 0
    if created_at:
        hours_old = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
        if hours_old < 24:
            time_bonus = 20
        elif hours_old < 72:
            time_bonus = 10

    # 标签加成
    label_bonus = 0
    priority_labels = {
        'bug': 5,
        'feature': 3,
        'has repro': 5,
        'priority-high': 10,
        'priority-critical': 15,
        'oncall': 10
    }

    for label in issue_data.get('labels', []):
        label_name = label.get('name', '')
        if label_name in priority_labels:
            label_bonus += priority_labels[label_name]

    heat_score = base_score + time_bonus + label_bonus
    return round(heat_score, 2)


def calculate_hn_heat_score(story_data: Dict) -> float:
    """计算 HN 讨论热度分数"""
    points = story_data.get('points', 0)
    comments = story_data.get('num_comments', 0)

    # 基础分数
    base_score = (points * 1.5) + (comments * 2)

    # 时间加成
    created_timestamp = story_data.get('created_at_i', 0)
    time_bonus = 0
    if created_timestamp:
        days_old = (datetime.now(timezone.utc).timestamp() - created_timestamp) / 86400
        if days_old < 1:
            time_bonus = 30
        elif days_old < 3:
            time_bonus = 15
        elif days_old < 7:
            time_bonus = 5

    heat_score = base_score + time_bonus
    return round(heat_score, 2)


# ============================================================================
# 评论抓取和筛选
# ============================================================================

class CommentFetcher:
    """评论抓取和智能筛选器"""

    @staticmethod
    def detect_solution(text: str) -> bool:
        """检测是否是解决方案"""
        if not text:
            return False

        solution_keywords = [
            "workaround", "solution", "fix", "solved", "works for me",
            "临时方案", "解决方法", "修复", "可以用", "有效"
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in solution_keywords)

    @staticmethod
    def detect_interesting(text: str) -> bool:
        """检测是否有趣/有价值"""
        if not text or len(text) < 80:
            return False

        # 包含代码块
        if "```" in text or "`" in text:
            return True

        # 包含链接（可能是参考资料）
        if "http" in text:
            return True

        # 包含技术关键词
        tech_keywords = [
            "API", "error", "debug", "code", "function", "implementation",
            "architecture", "performance", "optimization"
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for kw in tech_keywords if kw.lower() in text_lower)

        return keyword_count >= 2

    @staticmethod
    def calculate_comment_quality(comment_data: Dict) -> float:
        """计算评论质量分数"""
        score = 0

        # 点赞数权重最高
        score += comment_data.get('upvotes', 0) * 3

        # 长度加分（但不要太长）
        text_length = len(comment_data.get('body', ''))
        if 100 < text_length < 500:
            score += 10
        elif 500 <= text_length < 1000:
            score += 5

        # 是解决方案
        if comment_data.get('is_solution', False):
            score += 30

        # 有趣/有价值
        if comment_data.get('is_interesting', False):
            score += 15

        return round(score, 2)


# ============================================================================
# 版本工具函数
# ============================================================================

def fetch_version_info(changelog_url: str) -> Dict:
    """从 changelog 页面提取版本信息（简化版）"""
    import re
    from bs4 import BeautifulSoup

    logger.info("正在检测版本信息...")

    response = make_request(changelog_url)
    if not response:
        logger.error("Changelog 请求失败")
        return {
            'current': 'unknown',
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': changelog_url,
            'changes': []
        }

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        version_pattern = re.compile(r'v?\d+\.\d+\.\d+')

        page_text = soup.get_text()
        all_versions = version_pattern.findall(page_text)

        current_version = 'unknown'
        if all_versions:
            current_version = all_versions[0]
            if not current_version.startswith('v'):
                current_version = f'v{current_version}'

        logger.info(f"✓ 当前版本: {current_version}")

        return {
            'current': current_version,
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': changelog_url,
            'changes': []
        }

    except Exception as e:
        logger.error(f"解析版本信息失败: {e}")
        return {
            'current': 'unknown',
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': changelog_url,
            'changes': []
        }
