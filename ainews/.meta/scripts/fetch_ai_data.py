#!/usr/bin/env python3
"""
AI 生态数据采集脚本

扩展功能：
1. 多 AI 工具（Cursor, Copilot）
2. AI 模型排名（LMSYS Arena）
3. 多关键词新闻（AI, LLM, GPT等）

使用：
    python fetch_ai_data.py [--products cursor,copilot] [--rankings] [--news]
"""

import argparse
import json
import logging
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List

# 复用现有模块
sys.path.insert(0, os.path.dirname(__file__))
from fetch_data_v2 import (
    Config, make_request, calculate_issue_heat_score,
    calculate_hn_heat_score, CommentFetcher, fetch_version_info
)
from db_manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 多产品配置
# ============================================================================

PRODUCTS = {
    'claude-code': {
        'name': 'Claude Code',
        'github_repo': 'anthropics/claude-code',
        'heat_threshold': 30,
    },
    'cursor': {
        'name': 'Cursor',
        'github_search': 'getcursor/cursor OR cursor-ai',  # 可能的 repo
        'reddit': 'r/cursor',
        'heat_threshold': 20,
    },
    'copilot': {
        'name': 'GitHub Copilot',
        'github_search': 'github/copilot',
        'heat_threshold': 25,
    },
}

HN_KEYWORDS = ['Claude Code', 'Cursor', 'AI', 'LLM', 'GPT-4', 'Gemini', 'OpenAI']


# ============================================================================
# 多产品 Issues 抓取
# ============================================================================

def fetch_product_issues(product_id: str, lookback_days: int = 3) -> List[Dict]:
    """抓取特定产品的 GitHub Issues"""
    product = PRODUCTS.get(product_id)
    if not product:
        logger.warning(f"未知产品: {product_id}")
        return []

    logger.info(f"正在抓取 {product['name']} Issues...")

    # 如果有 github_repo，直接抓取
    if 'github_repo' in product:
        url = f"{Config.GITHUB_API_BASE}/repos/{product['github_repo']}/issues"
        params = {
            'state': 'all',
            'sort': 'updated',
            'direction': 'desc',
            'per_page': 10,
        }
    # 否则使用搜索
    elif 'github_search' in product:
        url = f"{Config.GITHUB_API_BASE}/search/issues"
        params = {
            'q': f"{product['github_search']} type:issue",
            'sort': 'updated',
            'order': 'desc',
            'per_page': 10,
        }
    else:
        logger.warning(f"{product['name']} 无 GitHub 配置")
        return []

    response = make_request(url, params=params)
    if not response:
        return []

    try:
        data = response.json()
        issues_raw = data.get('items', data) if 'items' in data else data

        issues = []
        for issue in issues_raw:
            if 'pull_request' in issue:
                continue

            issue_data = {
                'number': issue['number'],
                'title': issue['title'],
                'url': issue['html_url'],
                'state': issue['state'],
                'comments': issue['comments'],
                'reactions': issue.get('reactions', {'total_count': 0}),
                'labels': [{'name': label['name']} for label in issue.get('labels', [])],
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at'],
                'source': product_id
            }

            issue_data['heat_score'] = calculate_issue_heat_score(issue)

            if issue_data['heat_score'] >= product.get('heat_threshold', 20):
                issues.append(issue_data)

        issues.sort(key=lambda x: x['heat_score'], reverse=True)
        logger.info(f"✓ {product['name']}: {len(issues[:3])} 个热门 Issues")
        return issues[:3]

    except Exception as e:
        logger.error(f"抓取 {product['name']} 失败: {e}")
        return []


# ============================================================================
# 多关键词 HN 抓取
# ============================================================================

def fetch_hn_multi_keywords(keywords: List[str], lookback_days: int = 3) -> List[Dict]:
    """抓取多关键词 HN 讨论并去重"""
    logger.info(f"正在抓取 HN 讨论（关键词: {len(keywords)}个）...")

    all_discussions = {}  # 使用 objectID 去重

    for keyword in keywords:
        params = {
            'query': keyword,
            'tags': 'story',
            'hitsPerPage': 5,
        }

        response = make_request(Config.HN_ALGOLIA_API, params=params)
        if not response:
            continue

        try:
            data = response.json()
            for story in data.get('hits', []):
                obj_id = story['objectID']

                # 去重：只保留热度最高的
                if obj_id in all_discussions:
                    if story.get('points', 0) > all_discussions[obj_id]['points']:
                        all_discussions[obj_id] = story
                else:
                    all_discussions[obj_id] = story

        except Exception as e:
            logger.error(f"抓取 HN '{keyword}' 失败: {e}")

    # 转换为列表并计算热度
    discussions = []
    for story in all_discussions.values():
        discussion_data = {
            'objectID': story['objectID'],
            'title': story['title'],
            'url': story.get('url', ''),
            'hn_url': f"https://news.ycombinator.com/item?id={story['objectID']}",
            'points': story.get('points', 0),
            'comments': story.get('num_comments', 0),
            'author': story.get('author', ''),
            'created_at': story.get('created_at', ''),
            'keyword_matched': '未知'  # 可以记录匹配的关键词
        }

        discussion_data['heat_score'] = calculate_hn_heat_score(story)

        if discussion_data['heat_score'] >= 50:  # 降低阈值
            discussions.append(discussion_data)

    discussions.sort(key=lambda x: x['heat_score'], reverse=True)
    logger.info(f"✓ HN: {len(discussions[:5])} 个热门讨论（去重后）")
    return discussions[:5]


# ============================================================================
# 模型排名抓取（简化版）
# ============================================================================

def fetch_lmsys_rankings() -> List[Dict]:
    """抓取 LMSYS Arena 排名（需要 Firecrawl MCP，暂时返回模拟数据）"""
    logger.info("正在抓取 LMSYS Arena 排名...")
    logger.warning("⚠️  Firecrawl MCP 未集成，返回模拟数据")

    # 模拟数据（实际应使用 Firecrawl MCP）
    mock_rankings = [
        {'model': 'GPT-4-turbo', 'elo': 1253, 'rank': 1},
        {'model': 'Claude-3-opus', 'elo': 1248, 'rank': 2},
        {'model': 'Gemini-1.5-pro', 'elo': 1240, 'rank': 3},
        {'model': 'GPT-4o', 'elo': 1235, 'rank': 4},
        {'model': 'Claude-3.5-sonnet', 'elo': 1230, 'rank': 5},
    ]

    return mock_rankings


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='AI 生态数据采集脚本')
    parser.add_argument('--products', default='claude-code',
                        help='产品列表（逗号分隔，如 claude-code,cursor）')
    parser.add_argument('--rankings', action='store_true',
                        help='抓取模型排名')
    parser.add_argument('--news', action='store_true',
                        help='抓取 AI 新闻（多关键词）')
    parser.add_argument('--output', default='/Users/shenbo/Desktop/mind/ainews/.meta/cache/ai_data.json',
                        help='输出文件路径')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("AI 生态数据采集脚本")
    logger.info("=" * 60)

    # 初始化数据库
    db = DatabaseManager()

    # 1. 抓取多产品 Issues
    product_ids = [p.strip() for p in args.products.split(',')]
    all_issues = []

    for pid in product_ids:
        issues = fetch_product_issues(pid, lookback_days=3)
        for issue in issues:
            # 获取评论
            if 'github_repo' in PRODUCTS.get(pid, {}):
                repo = PRODUCTS[pid]['github_repo']
                # 这里简化，实际应传入 repo
                issue['top_comments'] = []
        all_issues.extend(issues)

    # 2. 抓取 HN 新闻（多关键词）
    discussions = []
    if args.news:
        discussions = fetch_hn_multi_keywords(HN_KEYWORDS, lookback_days=3)
    else:
        # 默认只抓取 Claude Code
        from fetch_data_v2 import fetch_hn_discussions
        discussions = fetch_hn_discussions(7, db)

    # 3. 抓取模型排名
    rankings = []
    if args.rankings:
        rankings = fetch_lmsys_rankings()

    # 4. 版本信息
    version = fetch_version_info(db)

    # 构建输出
    output_data = {
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': '3.0-ai'
        },
        'products': {
            pid: {'issues': [i for i in all_issues if i['source'] == pid]}
            for pid in product_ids
        },
        'rankings': rankings,
        'discussions': discussions,
        'version': version,
    }

    # 保存
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info("=" * 60)
    logger.info("采集完成！")
    logger.info(f"  产品: {len(product_ids)} 个")
    logger.info(f"  Issues: {len(all_issues)} 个")
    logger.info(f"  HN 讨论: {len(discussions)} 个")
    logger.info(f"  排名: {len(rankings)} 个")
    logger.info(f"  输出: {args.output}")
    logger.info("=" * 60)


if __name__ == '__main__':
    sys.exit(main())
