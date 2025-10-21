#!/usr/bin/env python3
"""
统一日志工具
支持：控制台输出、文件记录、日志轮转
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class MindLogger:
    """Mind 项目统一日志器"""

    def __init__(self, module_name: str, log_dir: str = None):
        """
        初始化日志器

        Args:
            module_name: 模块名称 (ccnews, ainews)
            log_dir: 日志目录，默认为 {module}/.meta/logs/
        """
        self.module_name = module_name

        # 设置日志目录
        if log_dir is None:
            project_root = Path(__file__).parent.parent
            log_dir = project_root / module_name / ".meta" / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 创建 logger
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的 handlers（避免重复）
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 添加 handlers
        self._add_console_handler()
        self._add_file_handler()

    def _add_console_handler(self):
        """添加控制台输出"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 彩色格式（可选）
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)

        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """添加文件输出（自动轮转）"""
        log_file = self.log_dir / f"{self.module_name}.log"

        # 5MB 轮转，保留 5 个备份
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 详细格式
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        self.logger.addHandler(file_handler)

    def info(self, msg: str):
        """INFO 级别日志"""
        self.logger.info(msg)

    def warning(self, msg: str):
        """WARNING 级别日志"""
        self.logger.warning(msg)

    def error(self, msg: str):
        """ERROR 级别日志"""
        self.logger.error(msg)

    def debug(self, msg: str):
        """DEBUG 级别日志"""
        self.logger.debug(msg)

    def critical(self, msg: str):
        """CRITICAL 级别日志"""
        self.logger.critical(msg)

    def log_execution(self, func_name: str, duration: float, success: bool = True):
        """记录执行统计"""
        status = "成功" if success else "失败"
        self.info(f"[执行统计] {func_name} - {status} - 耗时 {duration:.2f}s")

    def log_data_stats(self, data_type: str, count: int, details: dict = None):
        """记录数据统计"""
        msg = f"[数据统计] {data_type}: {count} 条"
        if details:
            msg += f" - {details}"
        self.info(msg)


# 便捷函数
def get_logger(module_name: str) -> MindLogger:
    """获取日志器实例"""
    return MindLogger(module_name)


if __name__ == "__main__":
    # 测试
    logger = get_logger("ccnews")

    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    logger.debug("这是一条 DEBUG 日志")

    logger.log_execution("fetch_data", 15.5, success=True)
    logger.log_data_stats("Issues", 3, {"热门": 2, "普通": 1})

    print(f"日志文件: {logger.log_dir}")
