#!/usr/bin/env python3
"""
报告质量检查工具

检查项：
1. 行数是否符合标准（80-120 行）
2. 是否包含必需的章节
3. 是否包含数据来源和引用
4. 格式是否正确
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


class ReportQualityChecker:
    """报告质量检查器"""

    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.content = ""
        self.lines = []
        self.issues = []

        if not self.report_path.exists():
            raise FileNotFoundError(f"报告文件不存在: {report_path}")

        self._load_content()

    def _load_content(self):
        """加载报告内容"""
        with open(self.report_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
            self.lines = self.content.split('\n')

    def check_length(self) -> bool:
        """检查行数（80-120 行）"""
        line_count = len(self.lines)

        if line_count < 80:
            self.issues.append(f"❌ 报告过短: {line_count} 行 (建议 80-120 行)")
            return False
        elif line_count > 120:
            self.issues.append(f"⚠️  报告过长: {line_count} 行 (建议 80-120 行)")
            return True  # 警告但不失败
        else:
            print(f"✅ 行数检查通过: {line_count} 行")
            return True

    def check_required_sections(self, module: str = 'ccnews') -> bool:
        """检查必需章节"""
        if module == 'ccnews':
            required_sections = [
                r'##\s+.*版本',
                r'##\s+.*Issue',
                r'##\s+.*社区',
            ]
        elif module == 'ainews':
            required_sections = [
                r'##\s+.*模型',
                r'##\s+.*新闻',
                r'##\s+.*社区',
                r'##\s+.*工具',
            ]
        else:
            return True

        missing_sections = []
        for pattern in required_sections:
            if not re.search(pattern, self.content, re.IGNORECASE):
                missing_sections.append(pattern)

        if missing_sections:
            self.issues.append(f"❌ 缺少必需章节: {missing_sections}")
            return False
        else:
            print(f"✅ 章节检查通过: {len(required_sections)} 个必需章节")
            return True

    def check_data_sources(self) -> bool:
        """检查是否包含数据来源"""
        # 检查是否有引用链接
        link_pattern = r'\[.*?\]\(https?://.*?\)'
        links = re.findall(link_pattern, self.content)

        if len(links) < 3:
            self.issues.append(f"⚠️  数据引用较少: {len(links)} 个链接 (建议 ≥ 3 个)")
            return True  # 警告但不失败
        else:
            print(f"✅ 数据来源检查通过: {len(links)} 个链接")
            return True

    def check_comments(self, module: str = 'ccnews') -> bool:
        """检查是否包含社区评论（仅 ccnews）"""
        if module != 'ccnews':
            return True

        # 检查是否有引用评论（> 格式）
        quote_pattern = r'^>\s+.*'
        quotes = [line for line in self.lines if re.match(quote_pattern, line)]

        if len(quotes) < 3:
            self.issues.append(f"❌ 社区评论不足: {len(quotes)} 条 (建议 ≥ 5 条)")
            return False
        else:
            print(f"✅ 评论检查通过: {len(quotes)} 条引用")
            return True

    def check_metadata(self) -> bool:
        """检查元数据（日期、版本等）"""
        has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}', self.content))
        has_version = bool(re.search(r'v\d+\.\d+\.\d+', self.content, re.IGNORECASE))

        if not has_date:
            self.issues.append("⚠️  未找到日期信息")

        if not has_version:
            self.issues.append("⚠️  未找到版本信息")

        return has_date and has_version

    def run_all_checks(self, module: str = 'ccnews') -> bool:
        """运行所有检查"""
        print(f"\n{'='*60}")
        print(f"报告质量检查: {self.report_path.name}")
        print(f"{'='*60}\n")

        checks = [
            ('行数', self.check_length()),
            ('章节', self.check_required_sections(module)),
            ('数据来源', self.check_data_sources()),
            ('元数据', self.check_metadata()),
        ]

        if module == 'ccnews':
            checks.append(('评论', self.check_comments(module)))

        # 统计结果
        passed = sum(1 for _, result in checks if result)
        total = len(checks)

        print(f"\n{'='*60}")
        print(f"检查完成: {passed}/{total} 项通过")

        if self.issues:
            print("\n⚠️  发现以下问题:")
            for issue in self.issues:
                print(f"  {issue}")

        print(f"{'='*60}\n")

        # 只要有一项失败就返回 False
        return all(result for _, result in checks)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python quality_check.py <report_path> [module]")
        print("示例: python quality_check.py cc/2025-10-18/index.md ccnews")
        sys.exit(1)

    report_path = sys.argv[1]
    module = sys.argv[2] if len(sys.argv) > 2 else 'ccnews'

    try:
        checker = ReportQualityChecker(report_path)
        success = checker.run_all_checks(module)

        sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
