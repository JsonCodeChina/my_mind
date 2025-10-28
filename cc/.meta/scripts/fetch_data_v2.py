#!/usr/bin/env python3
"""
Claude Code 数据采集脚本 V2 (优化版)

新功能：
1. 抓取 GitHub Issue 高赞评论
2. 抓取 HN 讨论评论
3. 数据存入 SQLite 数据库
4. 趋势分析（基于历史数据）
5. 智能评论筛选和打分

使用：
    python fetch_data_v2.py [--output OUTPUT_PATH] [--days LOOKBACK_DAYS]

依赖：
    pip install requests beautifulsoup4 python-dateutil
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import urljoin

# 导入数据库管理器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', '.shared/utils'))
from db_manager import DatabaseManager, predict_resolution_time

try:
    import requests
    from bs4 import BeautifulSoup
    from dateutil import parser as date_parser
except ImportError as e:
    print(f"错误: 缺少必需的依赖库 - {e}")
    print("请运行: pip install requests beautifulsoup4 python-dateutil")
    sys.exit(1)


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    # API URLs
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_REPO = "anthropics/claude-code"
    HN_ALGOLIA_API = "https://hn.algolia.com/api/v1/search"
    HN_ITEM_API = "https://hacker-news.firebaseio.com/v0/item"
    CHANGELOG_URL = "https://claudelog.com/claude-code-changelog/"

    # 默认参数
    DEFAULT_OUTPUT_PATH = "/Users/shenbo/Desktop/mind/cc/.meta/cache/daily_data.json"
    DEFAULT_GITHUB_LOOKBACK_DAYS = 3
    DEFAULT_HN_LOOKBACK_DAYS = 7

    # 筛选阈值
    ISSUE_HEAT_THRESHOLD = 30
    HN_HEAT_THRESHOLD = 70

    # 数量限制
    MAX_ISSUES = 3
    MAX_DISCUSSIONS = 2
    MAX_COMMENTS_PER_ISSUE = 10  # 每个 Issue 最多抓取多少评论

    # 请求超时
    REQUEST_TIMEOUT = 10

    # User-Agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


# ============================================================================
# 日志配置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


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
        'priority-critical': 15
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
    def fetch_github_comments(issue_number: int) -> List[Dict]:
        """抓取 GitHub Issue 的评论"""
        logger.info(f"  → 获取 Issue #{issue_number} 的评论...")

        url = f"{Config.GITHUB_API_BASE}/repos/{Config.GITHUB_REPO}/issues/{issue_number}/comments"
        params = {
            "per_page": 100,
            "sort": "created",
            "direction": "desc"
        }

        response = make_request(url, params=params)
        if not response:
            logger.warning(f"    获取评论失败: Issue #{issue_number}")
            return []

        try:
            comments_raw = response.json()

            # 如果没有评论，直接返回
            if not comments_raw:
                logger.info(f"    Issue #{issue_number} 无评论")
                return []

            comments = []
            for comment in comments_raw:
                comment_data = {
                    "author": comment['user']['login'],
                    "body": comment['body'][:1000],  # 限制长度
                    "upvotes": comment['reactions']['+1'],
                    "created_at": comment['created_at'],
                    "is_solution": CommentFetcher.detect_solution(comment['body']),
                    "is_interesting": CommentFetcher.detect_interesting(comment['body'])
                }

                # 计算质量分数
                comment_data['quality_score'] = CommentFetcher.calculate_comment_quality(comment_data)

                comments.append(comment_data)

            # 按质量分数排序
            comments.sort(key=lambda x: x['quality_score'], reverse=True)

            # 只保留高质量评论
            top_comments = [c for c in comments if c['quality_score'] > 10][:Config.MAX_COMMENTS_PER_ISSUE]

            logger.info(f"    ✓ 获取到 {len(comments)} 条评论，筛选出 {len(top_comments)} 条高质量评论")
            return top_comments

        except Exception as e:
            logger.error(f"解析评论失败: {e}")
            return []

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
        score += comment_data['upvotes'] * 3

        # 长度加分（但不要太长）
        text_length = len(comment_data['body'])
        if 100 < text_length < 500:
            score += 10
        elif 500 <= text_length < 1000:
            score += 5

        # 是解决方案
        if comment_data['is_solution']:
            score += 30

        # 有趣/有价值
        if comment_data['is_interesting']:
            score += 15

        return round(score, 2)


# ============================================================================
# 数据采集
# ============================================================================

def fetch_github_issues(lookback_days: int, db: DatabaseManager) -> List[Dict]:
    """从 GitHub API 获取最近的 Issues"""
    logger.info("正在获取 GitHub Issues...")

    since_date = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    url = f"{Config.GITHUB_API_BASE}/repos/{Config.GITHUB_REPO}/issues"
    params = {
        'state': 'all',
        'sort': 'updated',
        'direction': 'desc',
        'per_page': 30,
        'since': since_date
    }

    response = make_request(url, params=params)
    if not response:
        logger.error("GitHub API 请求失败")
        return []

    try:
        issues_raw = response.json()
        issues = []

        for issue in issues_raw:
            # 跳过 Pull Requests
            if 'pull_request' in issue:
                continue

            issue_data = {
                'number': issue['number'],
                'title': issue['title'],
                'url': issue['html_url'],
                'state': issue['state'],
                'comments': issue['comments'],
                'reactions': issue['reactions'],
                'labels': [{'name': label['name']} for label in issue['labels']],
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at']
            }

            # 计算热度分数
            issue_data['heat_score'] = calculate_issue_heat_score(issue)

            # 过滤低热度 Issues
            if issue_data['heat_score'] >= Config.ISSUE_HEAT_THRESHOLD:
                # 获取评论
                top_comments = CommentFetcher.fetch_github_comments(issue_data['number'])
                issue_data['top_comments'] = top_comments

                # 获取趋势数据
                trend_data = db.get_issue_trend(issue_data['number'], days=7)
                issue_data['trend'] = trend_data

                # 预测修复时间
                if trend_data:
                    issue_data['prediction'] = predict_resolution_time(
                        trend_data.get('comment_rate', 0),
                        issue_data['heat_score'],
                        issue_data['state']
                    )

                # 存入数据库
                db.insert_issue(issue_data)
                for comment in top_comments:
                    db.insert_comment(issue_data['number'], comment)

                issues.append(issue_data)

        # 按热度排序并限制数量
        issues.sort(key=lambda x: x['heat_score'], reverse=True)
        issues = issues[:Config.MAX_ISSUES]

        logger.info(f"✓ 获取到 {len(issues)} 个热门 Issues")
        return issues

    except Exception as e:
        logger.error(f"解析 GitHub 数据失败: {e}")
        return []


def fetch_hn_discussions(lookback_days: int, db: DatabaseManager) -> List[Dict]:
    """从 HN Algolia API 获取相关讨论"""
    logger.info("正在获取 Hacker News 讨论...")

    since_timestamp = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp())
    params = {
        'query': 'Claude Code',
        'tags': 'story',
        'numericFilters': f'created_at_i>{since_timestamp}'
    }

    response = make_request(Config.HN_ALGOLIA_API, params=params)
    if not response:
        logger.error("HN API 请求失败")
        return []

    try:
        data = response.json()
        discussions = []

        for story in data.get('hits', []):
            discussion_data = {
                'objectID': story['objectID'],
                'title': story['title'],
                'url': story.get('url', ''),
                'hn_url': f"https://news.ycombinator.com/item?id={story['objectID']}",
                'points': story.get('points', 0),
                'comments': story.get('num_comments', 0),
                'author': story.get('author', ''),
                'created_at': story.get('created_at', '')
            }

            # 计算热度分数
            discussion_data['heat_score'] = calculate_hn_heat_score(story)

            # 过滤低热度讨论
            if discussion_data['heat_score'] >= Config.HN_HEAT_THRESHOLD:
                # 存入数据库
                db.insert_discussion(discussion_data)
                discussions.append(discussion_data)

        # 按热度排序并限制数量
        discussions.sort(key=lambda x: x['heat_score'], reverse=True)
        discussions = discussions[:Config.MAX_DISCUSSIONS]

        logger.info(f"✓ 获取到 {len(discussions)} 个热门讨论")
        return discussions

    except Exception as e:
        logger.error(f"解析 HN 数据失败: {e}")
        return []


def fetch_version_info(db: DatabaseManager) -> Dict:
    """从 changelog 页面提取版本信息"""
    logger.info("正在检测版本信息...")

    response = make_request(Config.CHANGELOG_URL)
    if not response:
        logger.error("Changelog 请求失败")
        return {
            'current': 'unknown',
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': Config.CHANGELOG_URL,
            'changes': []
        }

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        version_pattern = re.compile(r'v?\d+\.\d+\.\d+')

        page_text = soup.get_text()
        all_versions = version_pattern.findall(page_text)

        current_version = 'unknown'
        release_date = datetime.now().strftime('%Y-%m-%d')

        if all_versions:
            current_version = all_versions[0]
            if not current_version.startswith('v'):
                current_version = f'v{current_version}'

        # 检查是否是新版本
        latest_in_db = db.get_latest_version('claude-code')
        is_new = False

        if latest_in_db:
            is_new = current_version != latest_in_db['version']
            if is_new:
                logger.info(f"🆕 检测到新版本: {latest_in_db['version']} → {current_version}")
                db.insert_version('claude-code', current_version, release_date)
        else:
            # 首次运行，插入当前版本
            db.insert_version('claude-code', current_version, release_date)

        logger.info(f"✓ 当前版本: {current_version}")

        return {
            'current': current_version,
            'release_date': release_date,
            'is_new': is_new,
            'changelog_url': Config.CHANGELOG_URL,
            'changes': []
        }

    except Exception as e:
        logger.error(f"解析版本信息失败: {e}")
        return {
            'current': 'unknown',
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': Config.CHANGELOG_URL,
            'changes': []
        }


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Claude Code 数据采集脚本 V2')
    parser.add_argument('--output', '-o', default=Config.DEFAULT_OUTPUT_PATH,
                        help=f'输出文件路径 (默认: {Config.DEFAULT_OUTPUT_PATH})')
    parser.add_argument('--github-days', type=int, default=Config.DEFAULT_GITHUB_LOOKBACK_DAYS,
                        help=f'GitHub Issues 回溯天数 (默认: {Config.DEFAULT_GITHUB_LOOKBACK_DAYS})')
    parser.add_argument('--hn-days', type=int, default=Config.DEFAULT_HN_LOOKBACK_DAYS,
                        help=f'HN 讨论回溯天数 (默认: {Config.DEFAULT_HN_LOOKBACK_DAYS})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细日志')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("Claude Code 数据采集脚本 V2 (优化版)")
    logger.info("=" * 60)

    # 初始化数据库
    db = DatabaseManager()

    # 采集数据
    start_time = datetime.now()

    issues = fetch_github_issues(args.github_days, db)
    discussions = fetch_hn_discussions(args.hn_days, db)
    version = fetch_version_info(db)

    # 构建输出数据
    output_data = {
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': '2.0'
        },
        'version': version,
        'issues': issues,
        'discussions': discussions,
        'articles': []
    }

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 写入文件
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ 数据已保存到: {args.output}")
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        return 1

    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    total_comments = sum(len(issue.get('top_comments', [])) for issue in issues)

    logger.info("=" * 60)
    logger.info("采集完成！")
    logger.info(f"  Issues: {len(issues)} 个")
    logger.info(f"  评论: {total_comments} 条")
    logger.info(f"  HN 讨论: {len(discussions)} 个")
    logger.info(f"  版本: {version['current']}")
    logger.info(f"  耗时: {elapsed_time:.2f} 秒")
    logger.info("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
