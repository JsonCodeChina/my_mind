#!/usr/bin/env python3
"""
Claude Code 每日数据采集脚本 (异步并行版本)

功能：
1. 从 GitHub API 获取热门 Issues
2. 从 HN Algolia API 获取相关讨论
3. 从社区文档站获取最新文章
4. 检测 Claude Code 版本更新
5. 计算热度评分并排序
6. 输出结构化 JSON 数据

使用：
    python fetch_data_async.py [--output OUTPUT_PATH]

依赖：
    pip install aiohttp beautifulsoup4 python-dateutil
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import aiohttp
    from bs4 import BeautifulSoup
    from dateutil import parser as date_parser
except ImportError as e:
    print(f"错误: 缺少必需的依赖库 - {e}")
    print("请运行: pip install aiohttp beautifulsoup4 python-dateutil")
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
    CHANGELOG_URL = "https://claudelog.com/claude-code-changelog/"
    COMMUNITY_DOCS_URL = "https://cc.deeptoai.com/docs"

    # 默认参数
    DEFAULT_OUTPUT_PATH = "/Users/shenbo/Desktop/mind/cc/cache/daily_data.json"
    DEFAULT_GITHUB_LOOKBACK_DAYS = 3
    DEFAULT_HN_LOOKBACK_DAYS = 7

    # 筛选阈值（优化后更严格）
    ISSUE_HEAT_THRESHOLD = 30  # 20 → 30
    HN_HEAT_THRESHOLD = 70     # 50 → 70
    ARTICLE_QUALITY_THRESHOLD = 70

    # 数量限制（优化后减少）
    MAX_ISSUES = 3            # 5 → 3
    MAX_DISCUSSIONS = 2       # 3 → 2
    MAX_ARTICLES = 2

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

async def async_make_request(session: aiohttp.ClientSession, url: str,
                             params: Optional[Dict] = None) -> Optional[str]:
    """
    异步发送 HTTP 请求，带重试机制

    Args:
        session: aiohttp会话
        url: 请求 URL
        params: 查询参数

    Returns:
        响应文本，失败返回 None
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {url[:50]}... - {e}")
            if attempt == max_retries - 1:
                logger.error(f"请求最终失败: {url}")
                return None
            await asyncio.sleep(1)  # 重试前等待1秒
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
# 异步数据采集函数
# ============================================================================

async def fetch_github_issues(session: aiohttp.ClientSession, lookback_days: int = Config.DEFAULT_GITHUB_LOOKBACK_DAYS) -> List[Dict]:
    """异步获取 GitHub Issues"""
    logger.info("正在获取 GitHub Issues...")

    since_date = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    url = f"{Config.GITHUB_API_BASE}/repos/{Config.GITHUB_REPO}/issues"
    params = {
        'state': 'all',
        'sort': 'updated',
        'direction': 'desc',
        'per_page': 30,  # 减少请求量 50→30
        'since': since_date
    }

    response_text = await async_make_request(session, url, params=params)
    if not response_text:
        logger.error("GitHub API 请求失败")
        return []

    try:
        issues_raw = json.loads(response_text)
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
                'labels': [{'name': label['name']} for label in issue['labels'][:3]],  # 只保留前3个标签
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at']
            }

            # 计算热度分数
            issue_data['heat_score'] = calculate_issue_heat_score(issue)

            # 过滤低热度 Issues
            if issue_data['heat_score'] >= Config.ISSUE_HEAT_THRESHOLD:
                issues.append(issue_data)

        # 按热度排序并限制数量
        issues.sort(key=lambda x: x['heat_score'], reverse=True)
        issues = issues[:Config.MAX_ISSUES]

        logger.info(f"✓ 获取到 {len(issues)} 个热门 Issues")
        return issues

    except Exception as e:
        logger.error(f"解析 GitHub 数据失败: {e}")
        return []


async def fetch_hn_discussions(session: aiohttp.ClientSession, lookback_days: int = Config.DEFAULT_HN_LOOKBACK_DAYS) -> List[Dict]:
    """异步获取 HN 讨论"""
    logger.info("正在获取 Hacker News 讨论...")

    since_timestamp = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp())
    params = {
        'query': 'Claude Code',
        'tags': 'story',
        'numericFilters': f'created_at_i>{since_timestamp}'
    }

    response_text = await async_make_request(session, Config.HN_ALGOLIA_API, params=params)
    if not response_text:
        logger.error("HN API 请求失败")
        return []

    try:
        data = json.loads(response_text)
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
                discussions.append(discussion_data)

        # 按热度排序并限制数量
        discussions.sort(key=lambda x: x['heat_score'], reverse=True)
        discussions = discussions[:Config.MAX_DISCUSSIONS]

        logger.info(f"✓ 获取到 {len(discussions)} 个热门讨论")
        return discussions

    except Exception as e:
        logger.error(f"解析 HN 数据失败: {e}")
        return []


async def fetch_version_info(session: aiohttp.ClientSession) -> Dict:
    """异步获取版本信息"""
    logger.info("正在检测版本信息...")

    response_text = await async_make_request(session, Config.CHANGELOG_URL)
    if not response_text:
        logger.error("Changelog 请求失败")
        return {
            'current': 'unknown',
            'release_date': datetime.now().strftime('%Y-%m-%d'),
            'is_new': False,
            'changelog_url': Config.CHANGELOG_URL,
            'changes': []
        }

    try:
        soup = BeautifulSoup(response_text, 'html.parser')

        # 更灵活的版本号匹配
        version_pattern = re.compile(r'v?\d+\.\d+\.\d+')

        # 在页面文本中查找所有版本号
        page_text = soup.get_text()
        all_versions = version_pattern.findall(page_text)

        current_version = 'unknown'
        release_date = datetime.now().strftime('%Y-%m-%d')

        if all_versions:
            # 取第一个版本号（通常是最新的）
            current_version = all_versions[0]
            if not current_version.startswith('v'):
                current_version = f'v{current_version}'

        logger.info(f"✓ 当前版本: {current_version}")

        return {
            'current': current_version,
            'release_date': release_date,
            'is_new': False,  # 需要与 baseline 对比
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

async def async_main(args):
    """异步主函数"""
    logger.info("=" * 60)
    logger.info("Claude Code 每日数据采集脚本 (异步并行版)")
    logger.info("=" * 60)

    # 采集数据
    start_time = datetime.now()

    # 创建 aiohttp 会话
    headers = {"User-Agent": Config.USER_AGENT}
    async with aiohttp.ClientSession(headers=headers) as session:
        # 并行执行所有请求
        issues_task = fetch_github_issues(session, args.github_days)
        discussions_task = fetch_hn_discussions(session, args.hn_days)
        version_task = fetch_version_info(session)

        # 等待所有任务完成
        issues, discussions, version = await asyncio.gather(
            issues_task,
            discussions_task,
            version_task
        )

    # 构建输出数据
    output_data = {
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': '2.0'  # 异步版本标记
        },
        'version': version,
        'issues': issues,
        'discussions': discussions,
        'articles': []  # 简化：暂不抓取文章
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
    logger.info("=" * 60)
    logger.info("采集完成！")
    logger.info(f"  Issues: {len(issues)} 个")
    logger.info(f"  HN 讨论: {len(discussions)} 个")
    logger.info(f"  版本: {version['current']}")
    logger.info(f"  耗时: {elapsed_time:.2f} 秒")
    logger.info("=" * 60)

    return 0


def main():
    """主函数入口"""
    parser = argparse.ArgumentParser(description='Claude Code 每日数据采集脚本 (异步版)')
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

    # 运行异步主函数
    return asyncio.run(async_main(args))


if __name__ == '__main__':
    sys.exit(main())
