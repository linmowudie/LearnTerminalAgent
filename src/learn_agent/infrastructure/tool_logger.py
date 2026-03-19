"""
工具调用日志装饰器模块

为 LangChain @tool 装饰的函数提供日志记录功能，记录：
- 调用时间戳
- 函数名称
- 请求参数（敏感信息自动掩码）
- 执行耗时
- 返回结果摘要
- 异常信息

用法:
    from langchain_core.tools import tool
    from .tool_logger import log_tool_call
    
    @tool
    @log_tool_call
    def bash(command: str) -> str:
        ...
"""

from functools import wraps
from datetime import datetime
from typing import Any, List, Optional
import time
import json

from .logger import logger_tools
from ..core.config import get_config


def _mask_sensitive_value(value: str) -> str:
    """
    对敏感值进行掩码处理
    
    Args:
        value: 原始字符串值
        
    Returns:
        掩码后的字符串
    """
    if not value or len(value) < 8:
        return "*" * len(value) if value else ""
    
    # 显示前 4 位和后 4 位
    show_chars = 4
    middle_len = len(value) - show_chars * 2
    return f"{value[:show_chars]}{'*' * middle_len}{value[-show_chars:]}"


def _format_params(
    args: tuple,
    kwargs: dict,
    func_name: str,
    sensitive_params: Optional[List[str]] = None
) -> str:
    """
    格式化函数参数为日志字符串，敏感参数自动掩码
    
    Args:
        args: 位置参数
        kwargs: 关键字参数
        func_name: 函数名称
        sensitive_params: 需要掩码的参数名列表
        
    Returns:
        格式化后的参数字符串
    """
    if sensitive_params is None:
        # 从配置加载默认敏感参数名
        try:
            config = get_config()
            sensitive_params = getattr(config, 'sensitive_param_names', [
                'api_key', 'apikey', 'password', 'passwd', 
                'secret', 'token', 'credential'
            ])
        except Exception:
            # 配置加载失败时使用默认值
            sensitive_params = [
                'api_key', 'apikey', 'password', 'passwd', 
                'secret', 'token', 'credential'
            ]
    
    # 将敏感参数名转换为小写用于比较
    sensitive_params_lower = [p.lower() for p in sensitive_params]
    
    param_parts = []
    
    # 处理位置参数（通常工具函数的位置参数都有明确含义，直接显示）
    for i, arg in enumerate(args):
        arg_str = _format_arg_value(arg)
        param_parts.append(f"arg{i}={arg_str}")
    
    # 处理关键字参数
    for key, value in kwargs.items():
        key_lower = key.lower()
        
        # 检查是否需要掩码
        if any(s in key_lower for s in sensitive_params_lower):
            # 对敏感参数进行掩码处理
            if isinstance(value, str):
                masked_value = _mask_sensitive_value(value)
                param_parts.append(f"{key}={masked_value}")
            else:
                param_parts.append(f"{key}=***REDACTED***")
        else:
            # 普通参数正常显示
            param_parts.append(f"{key}={_format_arg_value(value)}")
    
    return ", ".join(param_parts)


def _format_arg_value(value: Any) -> str:
    """
    格式化单个参数值
    
    Args:
        value: 参数值
        
    Returns:
        格式化后的字符串表示
    """
    if value is None:
        return "None"
    
    if isinstance(value, str):
        # 字符串截断到合理长度
        max_len = 200
        if len(value) > max_len:
            return f'"{value[:max_len]}..." ({len(value)} chars)'
        return f'"{value}"'
    
    if isinstance(value, (int, float, bool)):
        return str(value)
    
    if isinstance(value, (list, tuple, set)):
        # 容器类型只显示长度和类型
        item_type = type(value[0]).__name__ if value else 'empty'
        return f"[{len(value)} {item_type}s]"
    
    if isinstance(value, dict):
        # 字典只显示键名和数量
        keys_preview = ", ".join(list(value.keys())[:3])
        if len(value) > 3:
            keys_preview += ", ..."
        return f"{{{keys_preview}}} ({len(value)} keys)"
    
    # 其他类型使用 repr
    return repr(value)


def _summarize_result(result: Any, max_length: int = 100) -> str:
    """
    生成返回结果的摘要
    
    Args:
        result: 函数返回值
        max_length: 最大显示长度
        
    Returns:
        结果摘要字符串
    """
    if result is None:
        return "None"
    
    if isinstance(result, str):
        if len(result) > max_length:
            return f'"{result[:max_length]}..." ({len(result)} chars)'
        return f'"{result}"'
    
    if isinstance(result, (int, float, bool)):
        return str(result)
    
    if isinstance(result, (list, tuple)):
        preview = ", ".join(str(item) for item in result[:3])
        if len(result) > 3:
            preview += ", ..."
        return f"[{preview}] ({len(result)} items)"
    
    if isinstance(result, dict):
        preview = ", ".join(f"{k}={v}" for k, v in list(result.items())[:3])
        if len(result) > 3:
            preview += ", ..."
        return f"{{{preview}}} ({len(result)} entries)"
    
    return repr(result)


def log_tool_call(func=None, *, sensitive_params: Optional[List[str]] = None):
    """
    工具调用日志装饰器
    
    记录工具的调用时间、参数、执行耗时和结果
    支持敏感参数自动掩码
    
    Args:
        func: 被装饰的函数
        sensitive_params: 需要掩码的参数名列表（可选，默认从配置读取）
        
    Returns:
        装饰后的函数
        
    用法示例:
        @tool
        @log_tool_call
        def bash(command: str) -> str:
            ...
        
        @tool
        @log_tool_call(sensitive_params=['api_key', 'password'])
        def custom_tool(api_key: str, other_param: str) -> str:
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 记录调用开始
            start_time = time.time()
            timestamp = datetime.now().isoformat()
            
            # 构建参数字符串（敏感信息掩码）
            params_log = _format_params(args, kwargs, f.__name__, sensitive_params)
            
            try:
                # 记录调用开始
                logger_tools.info(
                    f"[TOOL_CALL] {f.__name__}({params_log})",
                    extra={'timestamp': timestamp}
                )
                
                # 执行原函数
                result = f(*args, **kwargs)
                
                # 记录成功和耗时
                elapsed = time.time() - start_time
                result_summary = _summarize_result(result)
                logger_tools.info(
                    f"[TOOL_SUCCESS] {f.__name__} completed in {elapsed:.3f}s, "
                    f"result: {result_summary}"
                )
                
                return result
                
            except Exception as e:
                # 记录异常
                elapsed = time.time() - start_time
                logger_tools.error(
                    f"[TOOL_ERROR] {f.__name__} failed after {elapsed:.3f}s: "
                    f"{type(e).__name__}: {str(e)}"
                )
                raise
        
        return wrapper
    
    if func:
        return decorator(func)
    return decorator


# ========== 便捷函数 ==========

def get_all_tool_names(tools_module) -> List[str]:
    """
    获取模块中所有被@tool 装饰的函数名称
    
    Args:
        tools_module: 工具模块对象
        
    Returns:
        工具函数名称列表
    """
    tool_names = []
    
    for name in dir(tools_module):
        obj = getattr(tools_module, name)
        # 检查是否是 LangChain tool（有 name 属性且可调用）
        if hasattr(obj, 'name') and callable(obj):
            tool_names.append(name)
    
    return tool_names
