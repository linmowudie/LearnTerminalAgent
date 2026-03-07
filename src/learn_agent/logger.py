"""
日志系统模块

提供统一的日志管理功能，支持：
- 多级别日志（DEBUG, INFO, WARNING, ERROR）
- 文件日志（自动输出到 logs 目录）
- 结构化日志格式
- 无终端输出（安静模式）
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    设置并返回 logger
    
    Args:
        name: logger 名称
        level: 日志级别（默认 INFO）
        log_file: 日志文件路径（如果为 None，则使用默认 logs 目录）
        
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 注意：移除控制台处理器，只保留文件输出
    # 所有日志将输出到 logs 目录，不在终端显示
    
    # 文件处理器（始终启用）
    # 如果没有指定 log_file，使用默认的 logs 目录
    if not log_file:
        # 创建 logs 目录
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/{name}_{timestamp}.log"
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 文件格式（简洁清晰）
    file_fmt = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)
    
    # 记录日志文件位置（便于查找）
    logger.info(f"日志文件：{log_file}")
    
    return logger


# ========== 全局 Logger 实例 ==========

# Agent 核心日志 - 输出到 logs/agent_*.log
logger_agent = setup_logger('Agent', logging.INFO)

# 工具执行日志 - 输出到 logs/tools_*.log
logger_tools = setup_logger('Tools', logging.INFO)

# 工作空间日志 - 输出到 logs/workspace_*.log
logger_workspace = setup_logger('Workspace', logging.INFO)

# 配置日志 - 输出到 logs/config_*.log
logger_config = setup_logger('Config', logging.INFO)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    获取自定义 logger
    
    Args:
        name: logger 名称
        level: 日志级别
        
    Returns:
        Logger 对象
    """
    return setup_logger(name, level)


def set_log_level(level: int):
    """
    设置所有 logger 的级别
    
    Args:
        level: 日志级别（logging.DEBUG/INFO/WARNING/ERROR）
    """
    for logger in [logger_agent, logger_tools, logger_workspace, logger_config]:
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)


# ========== 便捷函数 ==========

def debug(msg: str, module: str = 'agent'):
    """记录 DEBUG 日志"""
    if module == 'agent':
        logger_agent.debug(msg)
    elif module == 'tools':
        logger_tools.debug(msg)
    elif module == 'workspace':
        logger_workspace.debug(msg)


def info(msg: str, module: str = 'agent'):
    """记录 INFO 日志"""
    if module == 'agent':
        logger_agent.info(msg)
    elif module == 'tools':
        logger_tools.info(msg)
    elif module == 'workspace':
        logger_workspace.info(msg)


def warning(msg: str, module: str = 'agent'):
    """记录 WARNING 日志"""
    if module == 'agent':
        logger_agent.warning(msg)
    elif module == 'tools':
        logger_tools.warning(msg)
    elif module == 'workspace':
        logger_workspace.warning(msg)


def error(msg: str, module: str = 'agent'):
    """记录 ERROR 日志"""
    if module == 'agent':
        logger_agent.error(msg)
    elif module == 'tools':
        logger_tools.error(msg)
    elif module == 'workspace':
        logger_workspace.error(msg)


# ========== 上下文管理器 ==========

from contextlib import contextmanager

@contextmanager
def log_context(operation: str, module: str = 'agent'):
    """
    日志上下文管理器
    
    用法:
        with log_context("加载配置"):
            load_config()
    
    Args:
        operation: 操作描述
        module: 模块名称
    """
    info(f"开始：{operation}", module)
    try:
        yield
        info(f"完成：{operation}", module)
    except Exception as e:
        error(f"失败：{operation} - {e}", module)
        raise


# ========== 性能计时 ==========

import time
from functools import wraps

def timing(func):
    """
    性能计时装饰器
    
    用法:
        @timing
        def slow_function():
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        info(f"{func.__name__} 执行耗时：{elapsed:.3f}s", 'agent')
        return result
    return wrapper
