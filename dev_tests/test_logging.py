"""
测试日志系统
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from learn_agent.infrastructure.logger import (
    logger_agent, logger_tools, logger_workspace,
    info, debug, warning, error,
    log_context, timing,
    enable_file_logging,
    set_log_level
)
import logging

print("=" * 60)
print("日志系统测试")
print("=" * 60)

# 测试 1：基本日志输出
print("\n[测试 1] 基本日志输出")
print("-" * 60)
info("这是一条 INFO 日志")
debug("这是一条 DEBUG 日志")
warning("这是一条 WARNING 日志")
error("这是一条 ERROR 日志")

# 测试 2：不同模块的日志
print("\n[测试 2] 不同模块的日志")
print("-" * 60)
info("Agent 模块消息", module='agent')
info("工具模块消息", module='tools')
info("工作空间模块消息", module='workspace')

# 测试 3：上下文管理器
print("\n[测试 3] 上下文管理器")
print("-" * 60)
with log_context("测试操作"):
    print("执行某些操作...")
    import time
    time.sleep(0.5)

# 测试 4：性能计时
print("\n[测试 4] 性能计时装饰器")
print("-" * 60)

@timing
def slow_function():
    time.sleep(1.5)
    return "完成"

result = slow_function()
print(f"函数返回：{result}")

# 测试 5：启用文件日志
print("\n[测试 5] 启用文件日志")
print("-" * 60)
enable_file_logging(log_dir="test_logs")
info("这条日志会同时输出到控制台和文件")

# 测试 6：设置日志级别
print("\n[测试 6] 设置日志级别为 DEBUG")
print("-" * 60)
set_log_level(logging.DEBUG)
debug("这条 DEBUG 日志应该能看到")

# 测试 7：实际场景 - 工作空间操作
print("\n[测试 7] 模拟工作空间操作")
print("-" * 60)
from learn_agent.infrastructure.workspace import WorkspaceManager

workspace = WorkspaceManager()
workspace.initialize(str(Path.cwd()))

resolved = workspace.resolve_path("test.txt")
print(f"解析路径结果：{resolved}")

# 清理
import shutil
if Path("test_logs").exists():
    shutil.rmtree("test_logs")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)
print("\n提示：查看 logs/ 目录可以看到保存的日志文件")
