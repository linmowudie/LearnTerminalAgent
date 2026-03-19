"""
工具调用日志装饰器测试模块
"""

import sys
from pathlib import Path
from functools import wraps

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.learn_agent.infrastructure.tool_logger import log_tool_call


# 测试日志装饰器（不使用@tool，只测试日志功能）
@log_tool_call
def test_function(name: str, age: int, api_key: str = "secret123456") -> str:
    """测试函数"""
    return f"Hello {name}, age {age}"


@log_tool_call(sensitive_params=['password'])
def test_sensitive_function(username: str, password: str) -> str:
    """测试敏感参数函数"""
    return f"Logged in {username}"


def test_basic_logging():
    """测试基本日志记录"""
    print("\n=== Test 1: Basic logging ===")
    result = test_function("Alice", 25)
    print(f"Result: {result}")
    print("Check logs/tools_*.log for output\n")


def test_sensitive_param_masking():
    """测试敏感参数掩码"""
    print("\n=== Test 2: Sensitive parameter masking ===")
    result = test_function("Bob", 30, api_key="sk-very-long-api-key-12345")
    print(f"Result: {result}")
    print("Check that api_key is masked in logs\n")


def test_custom_sensitive_params():
    """测试自定义敏感参数"""
    print("\n=== Test 3: Custom sensitive parameters ===")
    # 使用关键字参数传递 password
    result = test_sensitive_function(username="user123", password="my-secret-password")
    print(f"Result: {result}")
    print("Check that password is masked in logs\n")


if __name__ == "__main__":
    print("Testing Tool Logger Decorator")
    print("=" * 60)
    
    try:
        test_basic_logging()
        test_sensitive_param_masking()
        test_custom_sensitive_params()
        
        print("=" * 60)
        print("All tests completed!")
        print("Check the logs/ directory for log files.\n")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
